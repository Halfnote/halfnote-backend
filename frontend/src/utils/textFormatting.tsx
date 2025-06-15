import React from 'react';

export const parseFormattedText = (text: string): React.ReactNode[] => {
  if (!text) return [];

  // Split text into lines first to preserve line breaks
  const lines = text.split('\n');
  
  const parseLine = (line: string, lineIndex: number): React.ReactNode => {
    if (line.trim() === '') {
      return <br key={`br-${lineIndex}`} />;
    }

    const parts: React.ReactNode[] = [];
    let remainingText = line;
    let partIndex = 0;

    while (remainingText.length > 0) {
      let found = false;

      // Bold: **text**
      const boldMatch = remainingText.match(/^\*\*(.*?)\*\*/);
      if (boldMatch) {
        parts.push(
          <strong key={`${lineIndex}-${partIndex++}`}>
            {boldMatch[1]}
          </strong>
        );
        remainingText = remainingText.slice(boldMatch[0].length);
        found = true;
      }

      // Strikethrough: ~~text~~
      if (!found) {
        const strikeMatch = remainingText.match(/^~~(.*?)~~/);
        if (strikeMatch) {
          parts.push(
            <span 
              key={`${lineIndex}-${partIndex++}`}
              style={{ textDecoration: 'line-through' }}
            >
              {strikeMatch[1]}
            </span>
          );
          remainingText = remainingText.slice(strikeMatch[0].length);
          found = true;
        }
      }

      // Underline: __text__
      if (!found) {
        const underlineMatch = remainingText.match(/^__(.*?)__/);
        if (underlineMatch) {
          parts.push(
            <span 
              key={`${lineIndex}-${partIndex++}`}
              style={{ textDecoration: 'underline' }}
            >
              {underlineMatch[1]}
            </span>
          );
          remainingText = remainingText.slice(underlineMatch[0].length);
          found = true;
        }
      }

      // Italic: *text* (but not part of **)
      if (!found) {
        const italicMatch = remainingText.match(/^(?<!\*)\*([^*]+?)\*(?!\*)/);
        if (italicMatch) {
          parts.push(
            <em key={`${lineIndex}-${partIndex++}`}>
              {italicMatch[1]}
            </em>
          );
          remainingText = remainingText.slice(italicMatch[0].length);
          found = true;
        }
      }

      // No formatting found, take one character
      if (!found) {
        let nextFormatIndex = remainingText.length;
        
        // Find the next formatting character
        const nextBold = remainingText.indexOf('**');
        const nextStrike = remainingText.indexOf('~~');
        const nextUnderline = remainingText.indexOf('__');
        const nextItalic = remainingText.search(/(?<!\*)\*(?!\*)/);
        
        [nextBold, nextStrike, nextUnderline, nextItalic].forEach(index => {
          if (index !== -1 && index < nextFormatIndex) {
            nextFormatIndex = index;
          }
        });
        
        const plainText = remainingText.slice(0, nextFormatIndex || remainingText.length);
        if (plainText) {
          parts.push(plainText);
        }
        remainingText = remainingText.slice(plainText.length);
      }
    }

    return (
      <span key={`line-${lineIndex}`}>
        {parts}
      </span>
    );
  };

  return lines.map((line, index) => (
    <React.Fragment key={`fragment-${index}`}>
      {index > 0 && <br />}
      {parseLine(line, index)}
    </React.Fragment>
  ));
};

export const renderFormattedText = (text: string): React.ReactNode => {
  const parsed = parseFormattedText(text);
  return <>{parsed}</>;
}; 