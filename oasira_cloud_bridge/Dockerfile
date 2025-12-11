#============================#
#   OASIRA ADDON DOCKERFILE  #
#============================#
# This Dockerfile is not used when build.json is present
# Home Assistant pulls pre-built images from Docker Hub via build.json
# The actual images are built separately and pushed to effortlesshome/oasiracloudbridge

ARG BUILD_FROM
FROM ${BUILD_FROM}

# This is a placeholder Dockerfile required by Home Assistant
# The actual addon uses pre-built images specified in build.json:
# - effortlesshome/oasiracloudbridge:latest-amd64
# - effortlesshome/oasiracloudbridge:latest-aarch64

# Labels for Home Assistant
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_DESCRIPTION
ARG BUILD_NAME
ARG BUILD_REF
ARG BUILD_REPOSITORY
ARG BUILD_VERSION

LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="Oasira (https://github.com/EffortlessHome)"

