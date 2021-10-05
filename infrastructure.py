from typing import Protocol, Type
import troposphere.elasticloadbalancingv2 as elb
import troposphere.ec2 as ec2


from troposphere import (
    Base64,
    FindInMap,
    GetAtt,
    Join,
    Output,
    Parameter,
    Ref,
    Tags,
    Template,
)
from troposphere.autoscaling import Metadata
from troposphere.cloudformation import (
    Init,
    InitConfig,
    InitFile,
    InitFiles,
    InitService,
    InitServices,
)
from troposphere.ec2 import (
    EIP,
    VPC,
    Instance,
    InternetGateway,
    NetworkAcl,
    NetworkAclEntry,
    NetworkInterfaceProperty,
    PortRange,
    Route,
    RouteTable,
    SecurityGroup,
    SecurityGroupRule,
    Subnet,
    SubnetNetworkAclAssociation,
    SubnetRouteTableAssociation,
    VPCGatewayAttachment,
)
from troposphere.policies import CreationPolicy, ResourceSignal

t = Template()

# Mapping
t.add_mapping('RegionMap',{
    "us-east-1":    {"32":  "ami-087c17d1fe0178315"},
    "ap-south-1":    {"32":  "ami-0a23ccb2cdd9286bb"},
})


# Create a single VPC
vpc = t.add_resource(
    VPC(
        'VPC',
        CidrBlock="10.0.0.0/16",
        Tags=Tags(
            Name="My-VPC"
        )
    )
)


# Create a public subnet 0
public_subnet_0 = t.add_resource(
    Subnet(
        "PublicSubnet0",
        VpcId=Ref(vpc),
        CidrBlock="10.0.10.0/24",
        MapPublicIpOnLaunch=True,
        AvailabilityZone=Join("", [Ref("AWS::Region"), "a"]),
        Tags=Tags(
            Name="My-public-subnet-0"
        )
    )
)

# Create a public subnet 1
public_subnet_1 = t.add_resource(
    Subnet(
        "PublicSubnet1",
        VpcId=Ref(vpc),
        CidrBlock="10.0.20.0/24",
        MapPublicIpOnLaunch=True,
        AvailabilityZone=Join("", [Ref("AWS::Region"), "b"]),
        Tags=Tags(
            Name="My-public-subnet-1"
        )
    )
)

# Create a private subnet 0
private_subnet_0 = t.add_resource(
    Subnet(
        "PrivateSubnet0",
        VpcId=Ref(vpc),
        CidrBlock="10.0.50.0/24",
        MapPublicIpOnLaunch=False,
        AvailabilityZone=Join("", [Ref("AWS::Region"), "a"]),
        Tags=Tags(
            Name="My-private-subnet-0"
        )
    )
)

# Create a private subnet 1
private_subnet_1 = t.add_resource(
    Subnet(
        "PrivateSubnet1",
        VpcId=Ref(vpc),
        CidrBlock="10.0.60.0/24",
        MapPublicIpOnLaunch=False,
        AvailabilityZone=Join("", [Ref("AWS::Region"), "b"]),
        Tags=Tags(
            Name="My-private-subnet-1"
        )
    )
)

# Create security group for public subnet
public_subnet_sg = t.add_resource(
    ec2.SecurityGroup(
        "PublicSecurityGroup",
        GroupDescription="Enable HTTP and SSH for inbound access to public Subnet",
        VpcId=Ref(vpc),
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(
                IpProtocol="tcp",
                FromPort="22",
                ToPort="22",
                CidrIp="0.0.0.0/0",
            ),
            ec2.SecurityGroupRule(
                IpProtocol="tcp",
                FromPort="80",
                ToPort="80",
                CidrIp="0.0.0.0/0",
            ),
        ],
    )
)

# Create security group for private subnet
private_subnet_sg = t.add_resource(
    ec2.SecurityGroup(
        "PrivateSecurityGroup",
        GroupDescription="Enable HTTP and SSH for inbound access to private Subnet",
        VpcId=Ref(vpc),
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(
                IpProtocol="tcp",
                FromPort="22",
                ToPort="22",
                SourceSecurityGroupId=GetAtt(public_subnet_sg, "GroupId"),
            ),
            ec2.SecurityGroupRule(
                IpProtocol="tcp",
                FromPort="80",
                ToPort="80",
                SourceSecurityGroupId=GetAtt(public_subnet_sg, "GroupId"),
            ),
        ],
    )
)


# Create internet gateway
internet_gateway = t.add_resource(
    InternetGateway(
        "InternetGateway",
        Tags=Tags(
            Name="My-internet-gateway"
        )    
    )
)


# Attach internet gateway with VPC
gateway_attachment = t.add_resource(
    VPCGatewayAttachment(
        "VPCGatewayAttachment",
        VpcId=Ref(vpc),
        InternetGatewayId=Ref(internet_gateway)
    ) 
)

# Create ALB
alb = t.add_resource(
    elb.LoadBalancer(
        "ALB",
        Scheme="internet-facing",
        Subnets=[Ref(public_subnet_0), Ref(public_subnet_1)],
        Tags=Tags(
            Name="My-ALB"
        )
    )
)

# Create EC2 instance
ec2_instance = t.add_resource(
    ec2.Instance(
        "EC2Instance",
        ImageId= FindInMap("RegionMap", Ref("AWS::Region"), "32"),
        SecurityGroupIds=[GetAtt(private_subnet_sg, "GroupId")],
        SubnetId=Ref(private_subnet_0),
        KeyName="simpl-key",
        InstanceType="t2.micro",
        UserData=Base64(
        Join("\n",["#!/bin/bash",
          "yum update -y ",
          "yum install nginx -y",
          "service nginx start",
          "echo \"<html><h1>Simpl Assignment WebPage</h1></html>\"> /var/www/html/index.html"]
          )
        )
    )
)



# Create Target Groups
target_group = t.add_resource(
    elb.TargetGroup(
        "TargetGroup",
        HealthCheckIntervalSeconds="30",
        HealthCheckProtocol="HTTP",
        HealthCheckTimeoutSeconds="10",
        HealthyThresholdCount="4",
        Matcher=elb.Matcher(
            HttpCode="200"),
        Name="MyTargetSopara1337",
        Port="8080",
        Protocol="HTTP",
        Targets=[elb.TargetDescription(
            Id=Ref(ec2_instance),
            Port="80")],
        UnhealthyThresholdCount="3",
        VpcId=Ref(vpc)
    )
)


# Create ALB listener 
alb_listener = t.add_resource(
    elb.Listener(
        "Listener",
        Port="80",
        Protocol="HTTP",
        LoadBalancerArn=Ref(alb),
        DefaultActions=[elb.Action(
            Type="forward",
            TargetGroupArn=Ref(target_group)
        )]
    )
)

print(t.to_yaml())
