import React from "react";
import { createRoot } from "react-dom/client";
import Index from "./routes/index";
import "./styles.css";

const mount = document.getElementById("home-react-root");
if (mount) createRoot(mount).render(<React.StrictMode><Index /></React.StrictMode>);
