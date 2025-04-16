import { marked } from "marked";

export function createMarkdownRenderder() {
  const renderer = new marked.Renderer();
  renderer.link = ({
    href,
    title,
    text,
  }: {
    href: string;
    title?: string | null;
    text: string;
  }): string => {
    const titleAttr = title ? ` title="${title}"` : "";
    return `<a target="_blank" rel="nofollow" href="${href}"${titleAttr}>${text}</a>`;
  };
  return renderer;
}
