import json

from dateutil.parser import parse as parse_date

from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase

SEVERITY_MAP = {
    '0': 'critical',       # Critical
    '1': 'major',          # Error
    '2': 'warning',        # Warning
    '3': 'informational',  # Informational
    '4': 'debug'           # Verbose
}

DEFAULT_SEVERITY_LEVEL = '3'  # 'warning'


class AzureLogMonitorWebhook(WebhookBase):
    """
    Microsoft Azure Monitor alerts webhook
    https://docs.microsoft.com/en-us/azure/azure-monitor/platform/alerts-webhooks
    """

    def incoming(self, query_string, payload):

        # Alerts (new)
        if 'data' in payload:
            if payload['schemaId'] == 'azureMonitorCommonAlertSchema':
                resource        = payload['data']['essentials']['monitoringService']
                create_time     = payload['data']['essentials']['firedDateTime']
                event           = payload['data']['essentials']['alertRule']
                service         = ['Microsoftoperational/Insights']
                group           = payload['data']['essentials']['signalType']
                event_type      = 'LogAnalyticAlert'
                text = '{} {} {} {}'.format(payload['data']['essentials']['signalType'], payload['data']['alertContext']['AlertType'], payload['data']['alertContext']['Operator'], payload['data']['alertContext']['Threshold'])
                value = '{}'.format(payload['data']['alertContext']['ResultCount']) 
                severity = 'major'
                environment = 'Production'
                tags = []
            else:
                text = '{}'.format(severity.upper())
                value = ''
                event_type = 'EventAlert'

        # Alerts (classic)
        else:
            context = payload['context']

            resource = context['resourceName']
            event = context['name']
            environment = query_string.get('environment', 'Production')

            if payload['status'] == 'Activated':
                severity = 'critical'
            elif payload['status'] == 'Resolved':
                severity = 'ok'
            else:
                severity = 'indeterminate'

            service = [context['resourceType']]
            group = context['resourceGroupName']

            if context['conditionType'] == 'Metric':
                condition = context['condition']
                text = '{}: {} {} ({} {})'.format(
                    severity.upper(),
                    condition['metricValue'],
                    condition['metricName'],
                    condition['operator'],
                    condition['threshold']
                )
                value = '{} {}'.format(
                    condition['metricValue'],
                    condition['metricName']
                )
            else:
                text = '{}'.format(severity.upper())
                value = ''

            tags = [] if payload['properties'] is None else ['{}={}'.format(k, v) for k, v in
                                                             payload['properties'].items()]
            event_type = '{}Alert'.format(context['conditionType'])
            create_time = parse_date(context['timestamp'])

        return Alert(
            resource=resource,
            event=event,
            environment=environment,
            severity=severity,
            service=service,
            group=group,
            value=value,
            text=text,
            tags=tags,
            attributes={},
            origin='Azure Monitor',
            type=event_type,
            create_time=create_time,
            raw_data=json.dumps(payload)
        )
