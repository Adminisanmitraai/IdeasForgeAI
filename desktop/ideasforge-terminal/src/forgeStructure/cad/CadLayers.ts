import type { CadLayer } from "./CadTypes";

export class CadLayers {
  private readonly layers: CadLayer[] = [
    {
      id: "grid",
      label: "Grid",
      visible: true,
    },
    {
      id: "axes",
      label: "Axes",
      visible: true,
    },
    {
      id: "structure",
      label: "Structure",
      visible: true,
    },
    {
      id: "dimensions",
      label: "Dimensions",
      visible: true,
    },
  ];

  isVisible(id: string): boolean {
    return (
      this.layers.find(
        (layer) => layer.id === id,
      )?.visible ?? false
    );
  }

  toggle(id: string): boolean {
    const layer = this.layers.find(
      (candidate) => candidate.id === id,
    );

    if (!layer) {
      return false;
    }

    layer.visible = !layer.visible;
    return layer.visible;
  }
}
