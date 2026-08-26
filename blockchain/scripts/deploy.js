const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying PlotProofRegistry with account:", deployer ? deployer.address : "local");

  const PlotProof = await hre.ethers.getContractFactory("PlotProofRegistry");
  const registry = await PlotProof.deploy();
  await registry.waitForDeployment();

  const address = await registry.getAddress();
  console.log("PlotProofRegistry successfully deployed to:", address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
