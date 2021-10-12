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
    NatGateway,
    NetworkAcl,
    NetworkAclEntry,
    NetworkInterfaceProperty,
    PortRange,
    Route,
    RouteTable,
    SecurityGroup,
    SecurityGroupRule,
    SecurityGroupIngress,
    SecurityGroupEgress,
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


# Nat Gateway EIP
nat_gateway_EIP = t.add_resource(EIP(
    "NatGatewayEIP",
    Domain = "vpc"
))


# Create Nat Gateway
nat_gateway = t.add_resource(NatGateway(
    "NatGateway",
    AllocationId = GetAtt(nat_gateway_EIP, 'AllocationId'),
    SubnetId = Ref(public_subnet_0)
))


# Create security group for public subnet
public_subnet_sg = t.add_resource(
    ec2.SecurityGroup(
        "PublicSecurityGroup",
        GroupDescription="Enable HTTP and SSH for inbound access to public Subnet",
        VpcId=Ref(vpc)
    )
)


# Create security group for private subnet
private_subnet_sg = t.add_resource(
    ec2.SecurityGroup(
        "PrivateSecurityGroup",
        GroupDescription="Enable HTTP and SSH for inbound access to private Subnet",
        VpcId=Ref(vpc)
    )
)


# Adding Ingress rule for private subnet security group 
t.add_resource(SecurityGroupIngress=[
    SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="22",
        ToPort="22",
        SourceSecurityGroupId=GetAtt(public_subnet_sg, "GroupId"),
        ),
    SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="80",
        ToPort="80",
        SourceSecurityGroupId=GetAtt(public_subnet_sg, "GroupId"),
        ),
    SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="443",
        ToPort="443",
        SourceSecurityGroupId=GetAtt(public_subnet_sg, "GroupId"),
        ),
    ],
    GroupId=Ref(private_subnet_sg)
)

# Adding Ingress rule for public subnet security group
t.add_resource(SecurityGroupEgress=[
    SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="22",
        ToPort="22",
        SourceSecurityGroupId=GetAtt(private_subnet_sg, "GroupId"),
        ),
    SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="80",
        ToPort="80",
        SourceSecurityGroupId=GetAtt(private_subnet_sg, "GroupId"),
        ),
    SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="443",
        ToPort="443",
        SourceSecurityGroupId=GetAtt(private_subnet_sg, "GroupId"),
        ),
    ],
    GroupId=Ref(public_subnet_sg)
)

# Adding Ingress rule for public subnet security group
t.add_resource(SecurityGrouIngress=[
    SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="22",
        ToPort="22",
        CidrIp="0.0.0.0/0",
            ),
    SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="80",
        ToPort="80",
        CidrIp="0.0.0.0/0",
            ),
    SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="443",
        ToPort="443",
        CidrIp="0.0.0.0/0",
        ),
    ],
    GroupId=Ref(public_subnet_sg)
)


# Create Public Route Table
public_route_table = t.add_resource(RouteTable(
    "PublicRouteTable",
    VpcId = Ref(vpc),
    Tags = Tags(
        Name = "Public-Route-Table"
    )
))

# Default Public Route for Public Route Table
t.add_resource(Route(
    "DefaultPublicRoute",
    DependsOn = gateway_attachment.title,
    RouteTableId = Ref(public_route_table),
    DestinationCidrBlock = "0.0.0.0/0",
    GatewayId = Ref(internet_gateway)
))

# Public Subnet Route Table Association
t.add_resource(SubnetRouteTableAssociation(
    "PublicSubnetRouteTableAssociation",
    RouteTableId = Ref(public_route_table),
    SubnetId = Ref(public_subnet_0)
))


# Private Route Table
private_route_table = t.add_resource(RouteTable(
    "PrivateRouteTable",
    VpcId = Ref(vpc),
    Tags = Tags(
        Name = "Private-Route-Table"
    )
))

# Default Private Route
t.add_resource(Route(
    "DefaultPrivateRoute",
    RouteTableId = Ref(private_route_table),
    DestinationCidrBlock = "0.0.0.0/0",
    NatGatewayId = Ref(nat_gateway)
))

# Private Subnet Route Table Association
t.add_resource(SubnetRouteTableAssociation(
    "PrivateSubnetRouteTableAssociation",
    RouteTableId = Ref(private_route_table),
    SubnetId = Ref(private_subnet_0)
))

# Create ALB
alb = t.add_resource(
    elb.LoadBalancer(
        "ALB",
        Scheme="internet-facing",
        Subnets=[Ref(public_subnet_0), Ref(public_subnet_1)],
        SecurityGroupIds=[GetAtt(public_subnet_sg, "GroupId")],
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
          "sudo yum update -y ",
          "sudo amazon-linux-extras install nginx1",
          "sudo systemctl start nginx",
          "sudo systectl enable nginx"]
          )
        )
    )
)


# Create Target Groups
target_group = t.add_resource(
    elb.TargetGroup(
        "TargetGroup",
        HealthCheckIntervalSeconds="300",
        HealthCheckProtocol="HTTP",
        HealthCheckTimeoutSeconds="120",
        HealthyThresholdCount="4",
        Matcher=elb.Matcher(
            HttpCode="200"),
        Name="MyTargetSopara1337",
        Port="80",
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
