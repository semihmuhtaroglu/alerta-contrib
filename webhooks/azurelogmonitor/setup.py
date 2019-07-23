from setuptools import setup, find_packages

version = '5.0.0'

setup(
    name="alerta-azure-logmonitor",
    version=version,
    description='Alerta webhook for Azure LogMonitor',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Anton Delitsch',
    author_email='anton@trugen.net',
    packages=find_packages(),
    py_modules=['alerta_azurelogmonitor'],
    install_requires=[
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.webhooks': [
            'azurelogmonitor = alerta_azurelogmonitor:AzureLogMonitorWebhook'
        ]
    }
)