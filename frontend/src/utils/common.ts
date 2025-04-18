import { marked } from "marked";
import { sha256 } from "js-sha256";

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

export const hash = (input: string) => {
  return sha256(input);
};
