import Image from "next/image";

type FigureProps = {
  src: string;
  alt: string;
  width: number;
  height: number;
  caption: string;
  source: string;
  priority?: boolean;
};

export function Figure({ src, alt, width, height, caption, source, priority = false }: FigureProps) {
  return (
    <figure className="figure">
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        priority={priority}
        sizes="(max-width: 1120px) 100vw, 1120px"
        style={{ width: "100%", height: "auto" }}
      />
      <figcaption>
        {caption}
        <cite>{source}</cite>
      </figcaption>
    </figure>
  );
}
