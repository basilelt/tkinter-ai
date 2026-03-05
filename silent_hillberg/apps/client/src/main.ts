import "./styles/global.css";
import { SilentHillbergApp } from "./app";

const root = document.getElementById("app");
if (!root) {
  throw new Error("Missing #app root");
}

const app = new SilentHillbergApp(root);

window.addEventListener("beforeunload", () => {
  app.destroy();
});
