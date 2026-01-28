import React from 'react';
import DOMPurify from 'dompurify';

interface SanitizedContentProps {
  content: string;
  className?: string;
  tagName?: 'div' | 'span' | 'p' | 'article' | 'section';
}

export default function SanitizedContent({ 
  content, 
  className = '', 
  tagName = 'div' 
}: SanitizedContentProps) {
  const sanitized = DOMPurify.sanitize(content);
  const Tag = tagName as any;

  return (
    <Tag 
      className={className}
      dangerouslySetInnerHTML={{ __html: sanitized }} 
    />
  );
}
