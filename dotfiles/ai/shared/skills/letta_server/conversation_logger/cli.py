"""
CLI interface for conversation logger.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import List, Optional

from .logger import ConversationLogger
from .config import Config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Conversation Logger - Save AI conversations to Letta server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Log a conversation from file
  %(prog)s log session-ses_2f34.md
  
  # Log from stdin
  echo "Conversation content" | %(prog)s log -
  
  # Start watching for conversation files
  %(prog)s watch --directories ~/workspace /tmp
  
  # Search conversations
  %(prog)s search "epstein project"
  
  # Show statistics
  %(prog)s stats
  
  # Export conversations
  %(prog)s export --format markdown --output ./exports
        """,
    )

    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Log command
    log_parser = subparsers.add_parser("log", help="Log a conversation")
    log_parser.add_argument("input", help='File path or "-" for stdin')
    log_parser.add_argument("--no-letta", action="store_true", help="Do not save to Letta server")
    log_parser.add_argument("--source", help="Source identifier")

    # Watch command
    watch_parser = subparsers.add_parser("watch", help="Watch for conversation files")
    watch_parser.add_argument("--directories", "-d", nargs="+", help="Directories to watch")
    watch_parser.add_argument(
        "--patterns", "-p", nargs="+", default=["*.md", "*.txt"], help="File patterns to watch"
    )

    # Search command
    search_parser = subparsers.add_parser("search", help="Search conversations")
    search_parser.add_argument("query", help="Search query")

    # Stats command
    subparsers.add_parser("stats", help="Show statistics")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export conversations")
    export_parser.add_argument(
        "--format", choices=["json", "markdown"], default="json", help="Export format"
    )
    export_parser.add_argument("--output", "-o", default="./exports", help="Output directory")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test Letta connection")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize logger
    logger = ConversationLogger(args.config)

    if args.verbose:
        logger.logger.setLevel("DEBUG")

    # Execute command
    try:
        if args.command == "log":
            cmd_log(logger, args)
        elif args.command == "watch":
            cmd_watch(logger, args)
        elif args.command == "search":
            cmd_search(logger, args)
        elif args.command == "stats":
            cmd_stats(logger, args)
        elif args.command == "export":
            cmd_export(logger, args)
        elif args.command == "test":
            cmd_test(logger, args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def cmd_log(logger: ConversationLogger, args):
    """Handle log command."""
    if args.input == "-":
        # Read from stdin
        print("Enter conversation (Ctrl+D to finish):")
        content = sys.stdin.read()
    else:
        # Read from file
        file_path = Path(args.input)
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            sys.exit(1)
        content = file_path.read_text(encoding="utf-8")

    # Process conversation
    result = logger.log_conversation(
        content=content, source=args.source or args.input, save_to_letta=not args.no_letta
    )

    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Conversation logged successfully!")
        print(f"   Session ID: {result['session_id']}")
        print(f"   Title: {result['title']}")
        print(f"   Messages: {result['message_count']}")
        print(f"   Key points: {len(result['key_points'])}")
        print(f"   Decisions: {len(result['decisions'])}")
        if not args.no_letta:
            print(f"   Saved to Letta server: Yes")


def cmd_watch(logger: ConversationLogger, args):
    """Handle watch command."""
    if args.directories:
        logger.config.set("monitoring", "watch_directories", value=args.directories)
    if args.patterns:
        logger.config.set("monitoring", "file_patterns", value=args.patterns)

    print("Starting conversation logger...")
    print("Press Ctrl+C to stop")
    print()

    logger.start_watching()

    try:
        while True:
            time.sleep(1)

            # Print periodic status
            stats = logger.get_stats()
            if stats["queue_size"] > 0:
                print(f"Queue: {stats['queue_size']} files waiting")

    except KeyboardInterrupt:
        print("\nStopping...")
        logger.stop_watching()
        print("Stopped.")


def cmd_search(logger: ConversationLogger, args):
    """Handle search command."""
    print(f"Searching for: {args.query}")

    results = logger.search_conversations(args.query)

    if not results:
        print("No results found")
        return

    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.get('text', '')[:100]}...")
        print(f"   Tags: {', '.join(result.get('tags', []))}")


def cmd_stats(logger: ConversationLogger, args):
    """Handle stats command."""
    stats = logger.get_stats()

    print("Conversation Logger Statistics")
    print("=" * 40)
    print(f"Running: {'Yes' if stats['is_running'] else 'No'}")
    print(f"Processed files: {stats['processed_files']}")
    print(f"Queue size: {stats['queue_size']}")
    print(f"Letta connected: {'Yes' if stats['letta_connected'] else 'No'}")
    print(f"Agent ID: {stats['agent_id']}")


def cmd_export(logger: ConversationLogger, args):
    """Handle export command."""
    print(f"Exporting conversations to {args.output}...")

    files = logger.export_archive(args.output, args.format)

    if files:
        print(f"Exported {len(files)} files:")
        for f in files:
            print(f"  - {f}")
    else:
        print("No files to export")


def cmd_test(logger: ConversationLogger, args):
    """Handle test command."""
    print("Testing Letta server connection...")

    if logger.letta_client.test_connection():
        print("✅ Letta server is connected!")

        # Test inserting a memory
        print("Testing memory insertion...")
        success = logger.letta_client.insert_memory(
            "Test memory from conversation logger", ["test", "conversation_logger"]
        )

        if success:
            print("✅ Memory insertion successful!")
        else:
            print("❌ Memory insertion failed")
    else:
        print("❌ Cannot connect to Letta server")
        print("Make sure Letta server is running: letta health")


if __name__ == "__main__":
    main()
