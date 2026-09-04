import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
// Renders pull heavy iframes/videos; a generous timeout avoids flaky hangs.
Config.setDelayRenderTimeoutInMilliseconds(60000);
