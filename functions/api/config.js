import handler from '../../netlify/functions/config.mjs';
import { wrap } from '../_lib/env.js';
export const onRequest = wrap(handler);
