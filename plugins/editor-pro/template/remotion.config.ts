import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(92);
Config.setOverwriteOutput(true);
Config.setDefaultPremountInSeconds(2);
// Windows: se o render falhar por caminho longo, use um Chrome headless num caminho curto:
// Config.setBrowserExecutable("C:/Users/<usuario>/.cache/rchs/chrome-headless-shell.exe");
