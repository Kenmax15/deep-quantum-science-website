import handler from '../../netlify/functions/capture-order.mjs';
import { wrap } from '../_lib/env.js';
export const onRequest = wrap(handler);
