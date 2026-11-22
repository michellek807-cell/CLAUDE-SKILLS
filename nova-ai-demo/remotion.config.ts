import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setConcurrency(2);
// If Remotion can't download its own browser on your machine, point it at Chrome:
// Config.setBrowserExecutable("/path/to/chrome");
