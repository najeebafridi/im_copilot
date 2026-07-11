import type { ReactElement } from "react";

import ReactMarkdown from "react-markdown";

interface MarkdownContentProps {
  content: string;
}

function isTableBlock(block: string): boolean {
  const lines = block.split("\n").map((line) => line.trim());
  if (lines.length < 2) {
    return false;
  }

  const header = lines[0];
  const divider = lines[1];
  return header.includes("|") && /^:?-{3,}:?(?:\s*\|\s*:?-{3,}:?)+$/.test(divider.replace(/\s+/g, ""));
}

function renderTable(block: string): ReactElement {
  const lines = block.split("\n").map((line) => line.trim()).filter(Boolean);
  const rows = lines.map((line) =>
    line
      .replace(/^\|/, "")
      .replace(/\|$/, "")
      .split("|")
      .map((cell) => cell.trim()),
  );
  const [header, , ...body] = rows;

  return (
    <table className="my-3 w-full border-collapse overflow-hidden rounded-xl border border-[var(--border)] text-sm">
      <thead className="bg-[var(--surface-2)]">
        <tr>
          {header.map((cell) => (
            <th key={cell} className="border border-[var(--border)] px-3 py-2 text-left font-semibold text-[var(--text)]">
              {cell}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {body.map((row, index) => (
          <tr key={`${index}-${row.join("-")}`} className="bg-[var(--surface)]">
            {row.map((cell) => (
              <td key={cell} className="border border-[var(--border)] px-3 py-2 text-[var(--text)]">
                {cell}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function MarkdownContent({ content }: MarkdownContentProps) {
  const blocks = content.split(/\n\s*\n/);

  return (
    <div className="space-y-3">
      {blocks.map((block, index) => {
        if (isTableBlock(block)) {
          return <div key={`${index}-table`}>{renderTable(block)}</div>;
        }

        return (
          <ReactMarkdown
            key={`${index}-md`}
            components={{
              h1: (props) => <h1 className="text-xl font-semibold text-[var(--text)]" {...props} />,
              h2: (props) => <h2 className="text-lg font-semibold text-[var(--text)]" {...props} />,
              h3: (props) => <h3 className="text-base font-semibold text-[var(--text)]" {...props} />,
              p: (props) => <p className="leading-6 text-[var(--text)]" {...props} />,
              strong: (props) => <strong className="font-semibold text-[var(--text)]" {...props} />,
              em: (props) => <em className="italic text-[var(--text)]" {...props} />,
              ul: (props) => <ul className="list-disc space-y-1 pl-5 text-[var(--text)]" {...props} />,
              ol: (props) => <ol className="list-decimal space-y-1 pl-5 text-[var(--text)]" {...props} />,
              blockquote: (props) => (
                <blockquote className="border-l-4 border-[var(--border)] pl-4 text-[var(--muted)]" {...props} />
              ),
              code: ({ className, children, ...props }) => (
                <code
                  className={`${className ?? ""} rounded bg-[var(--surface-2)] px-1.5 py-0.5 text-[0.95em] text-[var(--text)]`}
                  {...props}
                >
                  {children}
                </code>
              ),
              pre: (props) => (
                <pre className="overflow-x-auto rounded-xl border border-[var(--border)] bg-[var(--surface-2)] p-4 text-sm text-[var(--text)]" {...props} />
              ),
              a: (props) => (
                <a className="text-blue-600 underline underline-offset-2" target="_blank" rel="noreferrer" {...props} />
              ),
            }}
          >
            {block}
          </ReactMarkdown>
        );
      })}
    </div>
  );
}
