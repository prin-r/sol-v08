from brownie import accounts, StdReferenceBasic, StdReferenceProxy


def main():
    # load deployer account 0xa78dea8CE0744960EAcC14854EdBcbaf18B219Ed
    deployer = accounts.load("deployer")
    # deploy stdereferencebasic contract
    stdrefbasic = deployer.deploy(StdReferenceBasic)
    # deploy stdereferenceproxy contract
    deployer.deploy(StdReferenceProxy, stdrefbasic.address)
