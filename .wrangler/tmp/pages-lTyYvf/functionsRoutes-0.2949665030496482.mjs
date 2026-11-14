import { onRequestPost as __api_contact_js_onRequestPost } from "/home/claude/deep-quantum-science-website/functions/api/contact.js"
import { onRequest as __api_capture_order_js_onRequest } from "/home/claude/deep-quantum-science-website/functions/api/capture-order.js"
import { onRequest as __api_config_js_onRequest } from "/home/claude/deep-quantum-science-website/functions/api/config.js"
import { onRequest as __api_contact_js_onRequest } from "/home/claude/deep-quantum-science-website/functions/api/contact.js"
import { onRequest as __api_create_order_js_onRequest } from "/home/claude/deep-quantum-science-website/functions/api/create-order.js"

export const routes = [
    {
      routePath: "/api/contact",
      mountPath: "/api",
      method: "POST",
      middlewares: [],
      modules: [__api_contact_js_onRequestPost],
    },
  {
      routePath: "/api/capture-order",
      mountPath: "/api",
      method: "",
      middlewares: [],
      modules: [__api_capture_order_js_onRequest],
    },
  {
      routePath: "/api/config",
      mountPath: "/api",
      method: "",
      middlewares: [],
      modules: [__api_config_js_onRequest],
    },
  {
      routePath: "/api/contact",
      mountPath: "/api",
      method: "",
      middlewares: [],
      modules: [__api_contact_js_onRequest],
    },
  {
      routePath: "/api/create-order",
      mountPath: "/api",
      method: "",
      middlewares: [],
      modules: [__api_create_order_js_onRequest],
    },
  ]