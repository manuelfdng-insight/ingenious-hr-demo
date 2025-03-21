param (
    [string]$ImageName = "hr-ui:dev-uat",
    [string]$ContainerAppName = "hr-ui-app",
    [string]$DockerfilePath = "./docker/docker_file.dockerfile",
    [string]$ResourceGroup = "arg-syd-ing-dev-shared",
    [string]$AcrName = "acrsydingdevkfpqjli23em5m",
    [string]$ContainerAppEnvironment = "ingen-container-app-env"
)

# Azure Login
az login --tenant f23cc6fe-f058-410b-9edb-ff1b3b494e9f --use-device-code
az acr login --name $AcrName


# Build the Docker image for amd64 architecture
Write-Output "Building the Docker image for amd64 architecture..."
docker buildx create --use
if ($LASTEXITCODE -ne 0) {
    Write-Output "Error: Failed to initialize buildx."
    exit 1
}

docker buildx build --platform linux/amd64 -f $DockerfilePath -t $ImageName --output type=docker .
if ($LASTEXITCODE -ne 0) {
    Write-Output "Error: Failed to build the Docker image."
    exit 1
}

# Push the image to Azure Container Registry
Write-Output "Tagging and pushing the image to Azure Container Registry..."
docker tag $ImageName "$AcrName.azurecr.io/$ImageName"
docker push "$AcrName.azurecr.io/$ImageName"
if ($LASTEXITCODE -ne 0) {
    Write-Output "Error: Failed to push the image to Azure Container Registry."
    exit 1
}

# Confirmation
Write-Output "Image successfully built for amd64, pushed to Azure"