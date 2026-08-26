const hre = require("hardhat");

async function main() {
    console.log("Deploying PlotProofRegistry smart contract to network:", hre.network.name);

    const [deployer] = await hre.ethers.getSigners();
    console.log("Deploying with account:", deployer.address);

    const PlotProofRegistry = await hre.ethers.getContractFactory("PlotProofRegistry");
    const registry = await PlotProofRegistry.deploy(deployer.address);

    await registry.waitForDeployment();
    const address = await registry.getAddress();

    console.log("PlotProofRegistry successfully deployed to:", address);
    return address;
}

if (require.main === module) {
    main()
        .then(() => process.exit(0))
        .catch((error) => {
            console.error(error);
            process.exit(1);
        });
}

module.exports = main;
