import { marked } from "marked";

export const generateId = () => {
  return Date.now().toString() + Math.floor(Math.random() * 1000).toString();
};

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
