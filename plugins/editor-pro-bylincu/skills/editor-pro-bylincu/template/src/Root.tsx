import { Composition } from "remotion";
import roteiro from "../public/roteiro.json";
import { Video } from "./Video";
import type { Roteiro } from "./tipos";

const r = roteiro as Roteiro;

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Video"
    component={Video}
    durationInFrames={Math.max(1, r.duracaoQuadros)}
    fps={r.fps}
    width={r.largura}
    height={r.altura}
  />
);
