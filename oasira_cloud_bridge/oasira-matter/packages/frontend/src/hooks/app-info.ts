import { useMemo } from "react";
import packageJson from "../../../../apps/oasira-matter/package.json";

export interface AppInfo {
  name: string;
  version: string;
}

export function useAppInfo(): AppInfo {
  return useMemo(
    () => ({ name: packageJson.name, version: packageJson.version }),
    [],
  );
}
