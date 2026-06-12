/** Lucid web dashboard constants. */

export const DEFAULT_SAMPLE_RATE = 250;
export const DEFAULT_CHANNELS = 8;
// Use relative WebSocket URL — nginx proxies /ws/* to the server
export const SERVER_WS_URL = `ws://${window.location.host}/ws/viewer`;

/** Channel names following 10-20 system for default 8-channel montage. */
export const CHANNEL_NAMES = ['Fz', 'C3', 'Cz', 'C4', 'Pz', 'PO7', 'Oz', 'PO8'];
