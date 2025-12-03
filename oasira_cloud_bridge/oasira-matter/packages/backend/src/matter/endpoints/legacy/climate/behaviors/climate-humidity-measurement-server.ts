import type {
  ClimateDeviceAttributes,
  HomeAssistantEntityState,
} from "@oasira-matter/common";
import {
  type HumidityMeasurementConfig,
  HumidityMeasurementServer,
} from "../../../../behaviors/humidity-measurement-server.js";

const humidityConfig: HumidityMeasurementConfig = {
  getValue(entity: HomeAssistantEntityState) {
    const attributes = entity.attributes as ClimateDeviceAttributes;
    const humidity = attributes.current_humidity;
    if (humidity == null || Number.isNaN(+humidity)) {
      return null;
    }
    return +humidity;
  },
};

export const ClimateHumidityMeasurementServer =
  HumidityMeasurementServer(humidityConfig);
