import type { OpenSlideConfig } from '@open-slide/core';

const openSlideConfig: OpenSlideConfig = {
  base: process.env.DASHBOARD_BASE_PATH || '/',
  port: Number(process.env.DASHBOARD_PORT) || 5173,
};

export default openSlideConfig;
