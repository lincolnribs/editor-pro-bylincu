import React from "react";
import { Composition } from "raea";
import { r } from "./dados";
import { Video } from "./Video";

export const Raiz: React.FC = () => (
  <Composition id="Video" component={Video} durationInFrames={Math.max(1, Math.round(r.duracao * r.fps))} fps={r.fps} width={r.largura} height={r.altura} />
);
