import React, { useState, useRef } from 'react';
import styled from 'styled-components';

interface FormattedTextEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  minHeight?: string;
  disabled?: boolean;
}

const EditorContainer = styled.div`
  border: 1px solid #d1d5db;
  border-radius: 8px;
  overflow: hidden;
  
  &:focus-within {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const Toolbar = styled.div`
  display: flex;
  gap: 4px;
  padding: 8px 12px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  flex-wrap: wrap;
`;

const ToolbarButton = styled.button<{ $active?: boolean }>`
  background: ${props => props.$active ? '#e5e7eb' : 'transparent'};
  border: 1px solid ${props => props.$active ? '#9ca3af' : 'transparent'};
  border-radius: 4px;
  padding: 6px 8px;
  cursor: pointer;
  font-size: 12px;
  font-weight: ${props => props.$active ? '600' : '500'};
  color: #374151;
  transition: all 0.2s ease;
  min-width: 32px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: #e5e7eb;
    border-color: #9ca3af;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const TextArea = styled.textarea<{ minHeight?: string }>`
  width: 100%;
  padding: 12px;
  border: none;
  font-family: inherit;
  font-size: 14px;
  resize: vertical;
  min-height: ${props => props.minHeight || '120px'};
  outline: none;
  line-height: 1.5;

  &::placeholder {
    color: #9ca3af;
  }
`;

const FormatHint = styled.div`
  padding: 8px 12px;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  font-size: 11px;
  color: #6b7280;
  line-height: 1.4;
`;

const FormattedTextEditor: React.FC<FormattedTextEditorProps> = ({
  value,
  onChange,
  placeholder = "Write your text...",
  minHeight,
  disabled = false
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const insertFormatting = (before: string, after: string = '') => {
    if (!textareaRef.current || disabled) return;
    
    const textarea = textareaRef.current;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = value.substring(start, end);
    
    let newText: string;
    let newCursorPos: number;
    
    if (selectedText) {
      // Text is selected - wrap it
      newText = value.substring(0, start) + before + selectedText + after + value.substring(end);
      newCursorPos = start + before.length + selectedText.length + after.length;
    } else {
      // No selection - insert formatting markers
      newText = value.substring(0, start) + before + after + value.substring(end);
      newCursorPos = start + before.length;
    }
    
    onChange(newText);
    
    // Restore cursor position after React updates
    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus();
        textareaRef.current.setSelectionRange(newCursorPos, newCursorPos);
      }
    }, 0);
  };

  const formatBold = () => insertFormatting('**', '**');
  const formatItalic = () => insertFormatting('*', '*');
  const formatUnderline = () => insertFormatting('__', '__');
  const formatStrikethrough = () => insertFormatting('~~', '~~');

  // Check if cursor is within formatting
  const getActiveFormats = () => {
    if (!textareaRef.current) return {};
    
    const cursor = textareaRef.current.selectionStart;
    const beforeCursor = value.substring(0, cursor);
    const afterCursor = value.substring(cursor);
    
    return {
      bold: (beforeCursor.match(/\*\*/g) || []).length % 2 === 1,
      italic: (beforeCursor.match(/(?<!\*)\*(?!\*)/g) || []).length % 2 === 1,
      underline: (beforeCursor.match(/__/g) || []).length % 2 === 1,
      strikethrough: (beforeCursor.match(/~~/g) || []).length % 2 === 1,
    };
  };

  const activeFormats = getActiveFormats();

  return (
    <EditorContainer>
      <Toolbar>
        <ToolbarButton
          type="button"
          onClick={formatBold}
          disabled={disabled}
          $active={activeFormats.bold}
          title="Bold (**text**)"
        >
          <strong>B</strong>
        </ToolbarButton>
        
        <ToolbarButton
          type="button"
          onClick={formatItalic}
          disabled={disabled}
          $active={activeFormats.italic}
          title="Italic (*text*)"
        >
          <em>I</em>
        </ToolbarButton>
        
        <ToolbarButton
          type="button"
          onClick={formatUnderline}
          disabled={disabled}
          $active={activeFormats.underline}
          title="Underline (__text__)"
        >
          <u>U</u>
        </ToolbarButton>
        
        <ToolbarButton
          type="button"
          onClick={formatStrikethrough}
          disabled={disabled}
          $active={activeFormats.strikethrough}
          title="Strikethrough (~~text~~)"
        >
          <s>S</s>
        </ToolbarButton>
      </Toolbar>
      
      <TextArea
        ref={textareaRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        minHeight={minHeight}
        disabled={disabled}
      />
      

    </EditorContainer>
  );
};

export default FormattedTextEditor; 