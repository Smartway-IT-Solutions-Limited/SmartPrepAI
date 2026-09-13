import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

/**
 * Renders the AI tutor's answer: standard Markdown for structure/step lists,
 * plus \( ... \) / \[ ... \] LaTeX rendered inline via KaTeX. This is the
 * "Math Rendering" piece from the RAG blueprint.
 */
export default function MathMarkdown({ content }: { content: string }) {
  return (
    <div className="prose prose-invert max-w-none prose-p:leading-relaxed prose-headings:font-display">
      <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
        {content}
      </ReactMarkdown>
    </div>
  );
}
