import troposphere.elasticloadbalancingv2 as elb


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
        AvailabilityZone=Join("", [Ref("AWS::Region"), "a"]),
        Tags=Tags(
            Name="My-private-subnet-0"
        )
    )
)

# Create a private subnet 2
private_subnet_1 = t.add_resource(
    Subnet(
        "PrivateSubnet1",
        VpcId=Ref(vpc),
        CidrBlock="10.0.60.0/24",
        AvailabilityZone=Join("", [Ref("AWS::Region"), "b"]),
        Tags=Tags(
            Name="My-private-subnet-0"
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



print(t.to_yaml())
