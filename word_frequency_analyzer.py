"""
Word Frequency Analyzer
=======================
Analyzes word frequency in text files or direct input.
Supports case sensitivity, stopword exclusion, and top-N filtering.

Usage:
  python word_frequency_analyzer.py --file input.txt
  python word_frequency_analyzer.py --file input.txt --top 20 --no-stopwords
  python word_frequency_analyzer.py --file input.txt --case-sensitive --min-length 4
  python word_frequency_analyzer.py --text "Your text here"
"""

import re
import os
import sys
import json
import argparse
from collections import Counter
from pathlib import Path


# -----------------------------------------------------------------
# Stopwords list (English common words)
# -----------------------------------------------------------------
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to",
    "for", "of", "with", "by", "from", "is", "it", "its", "be", "as",
    "was", "are", "been", "were", "has", "have", "had", "do", "does",
    "did", "will", "would", "could", "should", "may", "might", "shall",
    "can", "not", "no", "nor", "so", "yet", "both", "either", "neither",
    "each", "every", "all", "any", "few", "more", "most", "other", "some",
    "such", "than", "then", "that", "this", "these", "those", "i", "me",
    "my", "we", "our", "you", "your", "he", "she", "her", "him", "his",
    "they", "them", "their", "what", "which", "who", "whom", "when",
    "where", "why", "how", "there", "here", "up", "out", "about", "into",
    "through", "during", "before", "after", "above", "below", "between",
    "own", "same", "just", "because", "while", "over", "under", "again",
    "further", "once", "also", "very", "too", "now", "new", "us", "am",
    "much", "many", "only",
}


# -----------------------------------------------------------------
# Core analysis functions (Python fundamentals)
# -----------------------------------------------------------------

def read_file(filepath: str) -> str:
    """Read text content from a file with error handling."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {filepath}")

    # Try UTF-8 first, fall back to latin-1
    for encoding in ("utf-8", "latin-1"):
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue

    raise IOError(f"Could not decode file: {filepath}")


def tokenize(text: str, case_sensitive: bool = False, min_length: int = 3) -> list[str]:
    """
    Extract word tokens from text using regex.
    - Strips punctuation and handles hyphenated / apostrophe words.
    - Applies case folding unless case_sensitive is True.
    """
    if not case_sensitive:
        text = text.lower()

    # Match words including those with internal hyphens/apostrophes
    raw_tokens = re.findall(r"\b[a-zA-ZÀ-ÿ][a-zA-ZÀ-ÿ'\-]*[a-zA-ZÀ-ÿ]\b|\b[a-zA-ZÀ-ÿ]\b", text)

    # Clean leading/trailing hyphens and apostrophes
    cleaned = [re.sub(r"^['\-]+|['\-]+$", "", t) for t in raw_tokens]

    # Filter by minimum length
    return [w for w in cleaned if len(w) >= min_length]


def count_frequencies(tokens: list[str], exclude_stopwords: bool = True) -> Counter:
    """Count word occurrences, optionally filtering stopwords."""
    if exclude_stopwords:
        tokens = [t for t in tokens if t.lower() not in STOPWORDS]
    return Counter(tokens)


def compute_statistics(text: str, tokens: list[str], freq: Counter) -> dict:
    """
    Compute summary statistics about the text.
    Returns a dict with counts and averages.
    """
    all_words = re.findall(r"\b\w+\b", text)
    sentences = len(re.findall(r"[^.!?]+[.!?]+", text)) or 1
    paragraphs = len([p for p in text.split("\n\n") if p.strip()])

    avg_word_length = (
        sum(len(w) for w in all_words) / len(all_words) if all_words else 0
    )

    return {
        "total_words": len(all_words),
        "unique_words": len(freq),
        "analyzed_tokens": len(tokens),
        "sentences": sentences,
        "paragraphs": max(paragraphs, 1),
        "avg_word_length": round(avg_word_length, 2),
        "lexical_richness": round(len(freq) / len(tokens), 4) if tokens else 0,
    }


def get_top_words(freq: Counter, top_n: int = 20) -> list[tuple[str, int]]:
    """Return top-N most common (word, count) pairs."""
    return freq.most_common(top_n)


# -----------------------------------------------------------------
# Output / display functions (file handling)
# -----------------------------------------------------------------

def print_statistics(stats: dict) -> None:
    """Print analysis statistics to stdout."""
    print("\n" + "=" * 50)
    print("  TEXT STATISTICS")
    print("=" * 50)
    print(f"  Total words       : {stats['total_words']:,}")
    print(f"  Unique words      : {stats['unique_words']:,}")
    print(f"  Analyzed tokens   : {stats['analyzed_tokens']:,}")
    print(f"  Sentences         : {stats['sentences']:,}")
    print(f"  Paragraphs        : {stats['paragraphs']:,}")
    print(f"  Avg word length   : {stats['avg_word_length']:.2f} chars")
    print(f"  Lexical richness  : {stats['lexical_richness']:.4f}")
    print("=" * 50)


def print_frequency_table(top_words: list[tuple[str, int]], max_bar: int = 30) -> None:
    """Print an ASCII frequency bar chart to stdout."""
    if not top_words:
        print("\n  No words to display.")
        return

    max_count = top_words[0][1]
    total = sum(c for _, c in top_words)

    print("\n  TOP WORDS\n")
    print(f"  {'#':<4} {'Word':<20} {'Count':>6}  {'%':>5}  {'Bar'}")
    print("  " + "-" * 60)

    for rank, (word, count) in enumerate(top_words, 1):
        bar_len = int((count / max_count) * max_bar)
        bar = "█" * bar_len
        pct = (count / total * 100) if total else 0
        print(f"  {rank:<4} {word:<20} {count:>6}  {pct:>4.1f}%  {bar}")

    print()


def save_results(
    output_path: str,
    stats: dict,
    top_words: list[tuple[str, int]],
    fmt: str = "txt",
) -> None:
    """
    Save analysis results to a file.
    Supports 'txt', 'csv', and 'json' formats.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        data = {
            "statistics": stats,
            "top_words": [{"word": w, "count": c} for w, c in top_words],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    elif fmt == "csv":
        with open(path, "w", encoding="utf-8") as f:
            f.write("rank,word,count,percentage\n")
            total = sum(c for _, c in top_words)
            for rank, (word, count) in enumerate(top_words, 1):
                pct = round(count / total * 100, 2) if total else 0
                f.write(f"{rank},{word},{count},{pct}\n")

    else:  # plain text
        with open(path, "w", encoding="utf-8") as f:
            f.write("WORD FREQUENCY ANALYSIS\n")
            f.write("=" * 50 + "\n\n")

            f.write("STATISTICS\n")
            for key, value in stats.items():
                f.write(f"  {key.replace('_', ' ').title():<22}: {value}\n")

            f.write("\nTOP WORDS\n")
            total = sum(c for _, c in top_words)
            for rank, (word, count) in enumerate(top_words, 1):
                pct = count / total * 100 if total else 0
                f.write(f"  {rank:>3}. {word:<20} {count:>6}  ({pct:.1f}%)\n")

    print(f"\n  Results saved to: {output_path}")


# -----------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------

def analyze(
    text: str,
    top_n: int = 20,
    case_sensitive: bool = False,
    exclude_stopwords: bool = True,
    min_length: int = 3,
    output_path: str | None = None,
    output_format: str = "txt",
    quiet: bool = False,
) -> dict:
    """
    Full analysis pipeline. Returns a results dict.

    Parameters
    ----------
    text             : Raw input text
    top_n            : Number of top words to return
    case_sensitive   : If True, 'Word' and 'word' are counted separately
    exclude_stopwords: If True, common English stopwords are excluded
    min_length       : Minimum character count for a token to be counted
    output_path      : Optional path to write results file
    output_format    : 'txt', 'csv', or 'json'
    quiet            : If True, suppress stdout output
    """
    tokens = tokenize(text, case_sensitive=case_sensitive, min_length=min_length)
    freq = count_frequencies(tokens, exclude_stopwords=exclude_stopwords)
    stats = compute_statistics(text, tokens, freq)
    top_words = get_top_words(freq, top_n=top_n)

    if not quiet:
        print_statistics(stats)
        print_frequency_table(top_words)

    if output_path:
        save_results(output_path, stats, top_words, fmt=output_format)

    return {"statistics": stats, "top_words": top_words}


def main():
    parser = argparse.ArgumentParser(
        description="Analyze word frequency in a text file or direct input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", "-f", metavar="PATH", help="Path to input text file")
    source.add_argument("--text", "-t", metavar="TEXT", help="Text string to analyze directly")

    parser.add_argument("--top", "-n", type=int, default=20, metavar="N",
                        help="Number of top words to display (default: 20)")
    parser.add_argument("--min-length", "-m", type=int, default=3, metavar="LEN",
                        help="Minimum word length to include (default: 3)")
    parser.add_argument("--case-sensitive", "-c", action="store_true",
                        help="Enable case-sensitive counting (default: off)")
    parser.add_argument("--no-stopwords", action="store_true",
                        help="Include stopwords in analysis (default: excluded)")
    parser.add_argument("--output", "-o", metavar="PATH",
                        help="Save results to this file path")
    parser.add_argument("--format", choices=["txt", "csv", "json"], default="txt",
                        help="Output file format: txt, csv, or json (default: txt)")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Suppress console output (use with --output)")

    args = parser.parse_args()

    # Load text
    if args.file:
        try:
            text = read_file(args.file)
            if not args.quiet:
                print(f"\n  Analyzing: {args.file}")
        except (FileNotFoundError, ValueError, IOError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        text = args.text

    if not text.strip():
        print("Error: Input text is empty.", file=sys.stderr)
        sys.exit(1)

    # Run analysis
    analyze(
        text=text,
        top_n=args.top,
        case_sensitive=args.case_sensitive,
        exclude_stopwords=not args.no_stopwords,
        min_length=args.min_length,
        output_path=args.output,
        output_format=args.format,
        quiet=args.quiet,
    )


if __name__ == "__main__":
    main()
