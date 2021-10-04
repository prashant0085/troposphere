import troposphere.ec2 as ec2
import troposphere.elasticloadbalancingv2 as elb

from troposphere import (
    Ref,
    Template,
    Tags,
    GetAtt,
    Join
)

from troposphere.ec2 import (
    Route,
    VPCGatewayAttachment, 
    SubnetRouteTableAssociation, 
    Subnet, 
    RouteTable, 
    VPC, 
    SubnetNetworkAclAssociation, 
    EIP, 
    InternetGateway
)


t = Template()

# Create a single VPC
vpc = t.add_resource(
    VPC(
        'VPC',
        CidrBlock="10.0.0.0/16",
        Tags=Tags(
            Name="My VPC"
        )
    )
)


# Create a public subnet
public_subnet = t.add_resource(
    Subnet(
        "PublicSubnet",
        VpcId=Ref(VPC),
        CidrBlock="10.0.10.0/24",
        MapPublicIpOnLaunch=True,
        AvailabilityZone=Join("", [Ref("AWS::Region"), "a"]),
        Tags=Tags(
            Name="My public subnet"
        )
    )
)


# Create a private subnet
public_subnet = t.add_resource(
    Subnet(
        "PrivateSubnet",
        VpcId=Ref(VPC),
        CidrBlock="10.0.20.0/24",
        AvailabilityZone=Join("", [Ref("AWS::Region"), "a"]),
        Tags=Tags(
            Name="My private subnet"
        )
    )
)


# Create internet gateway
internet_gateway = t.add_resource(
    InternetGateway(
        "InternetGateway",
    )
)

# Create a ALB
ALB = t.add_resoource()


print(t.to_yaml())
