import boto3.ec2

from boto3.ec2.elb import ELBConnection
from boto3.ec2.elb import HealthCheck

from boto3.ec2.autoscale import AutoScaleConnection
from boto3.ec2.autoscale import LaunchConfiguration
from boto3.ec2.autoscale import AutoScalingGroup
from boto3.ec2.autoscale import ScalingPolicy
from boto3.compat import json
from boto3.connection import AWSQueryConnection
from boto3.regioninfo import RegionInfo
from boto3.exception import JSONResponseError
from boto3.codedeploy import exceptions

AWS_ACCESS_KEY = ""
AWS_SECRET_KEY = ""
APIVersion = "2022-12-02"
DefaultRegionEndpoint = "codedeploy.ap-south-1.amazonaws.com"
ServiceName = "codedeploy"
TargetPrefix = "CodeDeploy_20221202"
ResponseError = JSONResponseError
region = "ap-south-1"

elastic_load_balancer = {
    "name": "my-load-balancer",
    "health_check_target": "HTTP:80/index.html",
    "connection_forwarding": [(80, 80, "http"), (443, 443, "tcp")],
    "timeout": 3,
    "interval": 20,
}

autoscaling_group = {
    "name": "auto_scale_test",
    "min_size": 1,
    "max_size": 2,
}

lc_name = "my_launch_config"

as_ami = {
    "id": "ami-baba68d3",
    "access_key": "seungjin-aws-main",
    "security_groups": ["seungjin-basic"],
    "instance_type": "t1.micro",
    "instance_monitoring": True,
}

conn_reg = boto.ec2.connect_to_region(region_name=region)
zones = conn_reg.get_all_zones()

zoneStrings = []
for zone in zones:
    zoneStrings.append(zone.name)

conn_elb = ELBConnection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
conn_as = AutoScaleConnection(AWS_ACCESS_KEY, AWS_SECRET_KEY)


hc = HealthCheck(
    "healthCheck",
    interval=elastic_load_balancer["interval"],
    target=elastic_load_balancer["health_check_target"],
    timeout=elastic_load_balancer["timeout"],
)

lb = conn_elb.create_load_balancer(
    elastic_load_balancer["name"],
    zoneStrings,
    elastic_load_balancer["connection_forwarding"],
)

lb.configure_health_check(hc)

lc = LaunchConfiguration(
    name=lc_name,
    image_id=as_ami["id"],
    key_name=as_ami["access_key"],
    security_groups=as_ami["security_groups"],
    instance_type=as_ami["instance_type"],
    instance_monitoring=as_ami["instance_monitoring"],
)

conn_as.create_launch_configuration(lc)


ag = AutoScalingGroup(
    group_name=autoscaling_group["name"],
    load_balancers=[elastic_load_balancer["name"]],
    availability_zones=zoneStrings,
    launch_config=lc,
    min_size=autoscaling_group["min_size"],
    max_size=autoscaling_group["max_size"],
)

conn_as.create_auto_scaling_group(ag)

scalingUpPolicy = ScalingPolicy(
    name="webserverScaleUpPolicy",
    adjustment_type="ChangeInCapacity",
    as_name=ag.name,
    scaling_adjustment=2,
    cooldown=180,
)

scalingDownPolicy = ScalingPolicy(
    name="webserverScaleDownPolicy",
    adjustment_type="ChangeInCapacity",
    as_name=ag.name,
    scaling_adjustment=-1,
    cooldown=180,
)

conn_as.create_scaling_policy(scalingUpPolicy)
conn_as.create_scaling_policy(scalingDownPolicy)


    def __init__(self, **kwargs):
        region = kwargs.pop("region", None)
        if not region:
            region = RegionInfo(
                self, self.region, self.DefaultRegionEndpoint
            )

        if "host" not in kwargs or kwargs["host"] is None:
            kwargs["host"] = region.endpoint

        super(CodeDeployConnection, self).__init__(**kwargs)
        self.region = region

    def _required_auth_capability(self):
        return ["hmac-v4"]

    def batch_get_applications(self, application_names=None):
         params = {}
        if application_names is not None:
            params["applicationNames"] = application_names
        return self.make_request(action="BatchGetApplications", body=json.dumps(params))

    def batch_get_deployments(self, deployment_ids=None):
        params = {}
        if deployment_ids is not None:
            params["deploymentIds"] = deployment_ids
        return self.make_request(action="BatchGetDeployments", body=json.dumps(params))

    def create_application(self, application_name):
        params = {
            "applicationName": application_name,
        }
        return self.make_request(action="CreateApplication", body=json.dumps(params))

    def create_deployment(
        self,
        application_name,
        deployment_group_name=None,
        revision=None,
        deployment_config_name=None,
        description=None,
        ignore_application_stop_failures=None,
    ):
        params = {
            "applicationName": application_name,
        }
        if deployment_group_name is not None:
            params["deploymentGroupName"] = deployment_group_name
        if revision is not None:
            params["revision"] = revision
        if deployment_config_name is not None:
            params["deploymentConfigName"] = deployment_config_name
        if description is not None:
            params["description"] = description
        if ignore_application_stop_failures is not None:
            params["ignoreApplicationStopFailures"] = ignore_application_stop_failures
        return self.make_request(action="CreateDeployment", body=json.dumps(params))

    def create_deployment_config(
        self, deployment_config_name, minimum_healthy_hosts=None
    ):
        params = {
            "deploymentConfigName": deployment_config_name,
        }
        if minimum_healthy_hosts is not None:
            params["minimumHealthyHosts"] = minimum_healthy_hosts
        return self.make_request(
            action="CreateDeploymentConfig", body=json.dumps(params)
        )

    def create_deployment_group(
        self,
        application_name,
        deployment_group_name,
        deployment_config_name=None,
        ec_2_tag_filters=None,
        auto_scaling_groups="auto_scale_test",
        service_role_arn=None,
    ):
        params = {
            "applicationName": application_name,
            "deploymentGroupName": deployment_group_name,
        }
        if deployment_config_name is not None:
            params["deploymentConfigName"] = deployment_config_name
        if ec_2_tag_filters is not None:
            params["ec2TagFilters"] = ec_2_tag_filters
        if auto_scaling_groups is not None:
            params["autoScalingGroups"] = auto_scaling_groups
        if service_role_arn is not None:
            params["serviceRoleArn"] = service_role_arn
        return self.make_request(
            action="CreateDeploymentGroup", body=json.dumps(params)
        )

    def delete_application(self, application_name):
        params = {
            "applicationName": application_name,
        }
        return self.make_request(action="DeleteApplication", body=json.dumps(params))

    def delete_deployment_config(self, deployment_config_name):
        params = {
            "deploymentConfigName": deployment_config_name,
        }
        return self.make_request(
            action="DeleteDeploymentConfig", body=json.dumps(params)
        )

    def delete_deployment_group(self, application_name, deployment_group_name):
        params = {
            "applicationName": application_name,
            "deploymentGroupName": deployment_group_name,
        }
        return self.make_request(
            action="DeleteDeploymentGroup", body=json.dumps(params)
        )

    def get_application(self, application_name):
        params = {
            "applicationName": application_name,
        }
        return self.make_request(action="GetApplication", body=json.dumps(params))

    def get_application_revision(self, application_name, revision):
        params = {
            "applicationName": application_name,
            "revision": revision,
        }
        return self.make_request(
            action="GetApplicationRevision", body=json.dumps(params)
        )

    def get_deployment(self, deployment_id):
        params = {
            "deploymentId": deployment_id,
        }
        return self.make_request(action="GetDeployment", body=json.dumps(params))

    def get_deployment_config(self, deployment_config_name):
        params = {
            "deploymentConfigName": deployment_config_name,
        }
        return self.make_request(action="GetDeploymentConfig", body=json.dumps(params))

    def get_deployment_group(self, application_name, deployment_group_name):
        params = {
            "applicationName": application_name,
            "deploymentGroupName": deployment_group_name,
        }
        return self.make_request(action="GetDeploymentGroup", body=json.dumps(params))

    def get_deployment_instance(self, deployment_id, instance_id):
        params = {
            "deploymentId": deployment_id,
            "instanceId": instance_id,
        }
        return self.make_request(
            action="GetDeploymentInstance", body=json.dumps(params)
        )

    def list_application_revisions(
        self,
        application_name,
        sort_by=None,
        sort_order=None,
        s_3_bucket=None,
        s_3_key_prefix=None,
        deployed=None,
        next_token=None,
    ):
        params = {
            "applicationName": application_name,
        }
        if sort_by is not None:
            params["sortBy"] = sort_by
        if sort_order is not None:
            params["sortOrder"] = sort_order
        if s_3_bucket is not None:
            params["s3Bucket"] = s_3_bucket
        if s_3_key_prefix is not None:
            params["s3KeyPrefix"] = s_3_key_prefix
        if deployed is not None:
            params["deployed"] = deployed
        if next_token is not None:
            params["nextToken"] = next_token
        return self.make_request(
            action="ListApplicationRevisions", body=json.dumps(params)
        )

    def list_applications(self, next_token=None):
        params = {}
        if next_token is not None:
            params["nextToken"] = next_token
        return self.make_request(action="ListApplications", body=json.dumps(params))

    def list_deployment_configs(self, next_token=None):
        params = {}
        if next_token is not None:
            params["nextToken"] = next_token
        return self.make_request(
            action="ListDeploymentConfigs", body=json.dumps(params)
        )

    def list_deployment_groups(self, application_name, next_token=None):
        params = {
            "applicationName": application_name,
        }
        if next_token is not None:
            params["nextToken"] = next_token
        return self.make_request(action="ListDeploymentGroups", body=json.dumps(params))

    def list_deployment_instances(
        self, deployment_id, next_token=None, instance_status_filter=None
    ):
        params = {
            "deploymentId": deployment_id,
        }
        if next_token is not None:
            params["nextToken"] = next_token
        if instance_status_filter is not None:
            params["instanceStatusFilter"] = instance_status_filter
        return self.make_request(
            action="ListDeploymentInstances", body=json.dumps(params)
        )

    def list_deployments(
        self,
        application_name=None,
        deployment_group_name=None,
        include_only_statuses=None,
        create_time_range=None,
        next_token=None,
    ):
        params = {}
        if application_name is not None:
            params["applicationName"] = application_name
        if deployment_group_name is not None:
            params["deploymentGroupName"] = deployment_group_name
        if include_only_statuses is not None:
            params["includeOnlyStatuses"] = include_only_statuses
        if create_time_range is not None:
            params["createTimeRange"] = create_time_range
        if next_token is not None:
            params["nextToken"] = next_token
        return self.make_request(action="ListDeployments", body=json.dumps(params))

    def register_application_revision(
        self, application_name, revision, description=None
    ):
        params = {
            "applicationName": application_name,
            "revision": revision,
        }
        if description is not None:
            params["description"] = description
        return self.make_request(
            action="RegisterApplicationRevision", body=json.dumps(params)
        )

    def stop_deployment(self, deployment_id):

        params = {
            "deploymentId": deployment_id,
        }
        return self.make_request(action="StopDeployment", body=json.dumps(params))

    def update_application(self, application_name=None, new_application_name=None):

        params = {}
        if application_name is not None:
            params["applicationName"] = application_name
        if new_application_name is not None:
            params["newApplicationName"] = new_application_name
        return self.make_request(action="UpdateApplication", body=json.dumps(params))

    def update_deployment_group(
        self,
        application_name,
        current_deployment_group_name,
        new_deployment_group_name=None,
        deployment_config_name=None,
        ec_2_tag_filters=None,
        auto_scaling_groups="auto_scale_test",
        service_role_arn=None,
    ):
        params = {
            "applicationName": application_name,
            "currentDeploymentGroupName": current_deployment_group_name,
        }
        if new_deployment_group_name is not None:
            params["newDeploymentGroupName"] = new_deployment_group_name
        if deployment_config_name is not None:
            params["deploymentConfigName"] = deployment_config_name
        if ec_2_tag_filters is not None:
            params["ec2TagFilters"] = ec_2_tag_filters
        if auto_scaling_groups is not None:
            params["autoScalingGroups"] = auto_scaling_groups
        if service_role_arn is not None:
            params["serviceRoleArn"] = service_role_arn
        return self.make_request(
            action="UpdateDeploymentGroup", body=json.dumps(params)
        )

    def make_request(self, action, body):
        headers = {
            "X-Amz-Target": "%s.%s" % (self.TargetPrefix, action),
            "Host": self.region.endpoint,
            "Content-Type": "application/x-amz-json-1.1",
            "Content-Length": str(len(body)),
        }
        http_request = self.build_base_http_request(
            method="POST",
            path="/",
            auth_path="/",
            params={},
            headers=headers,
            data=body,
        )
        response = self._mexe(http_request, sender=None, override_num_retries=10)
        response_body = response.read().decode("utf-8")
        boto.log.debug(response_body)
        if response.status == 200:
            if response_body:
                return json.loads(response_body)
        else:
            json_body = json.loads(response_body)
            fault_name = json_body.get("__type", None)
            exception_class = self._faults.get(fault_name, self.ResponseError)
            raise exception_class(response.status, response.reason, body=json_body)
