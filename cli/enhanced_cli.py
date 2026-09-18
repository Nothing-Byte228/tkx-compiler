"""Enhanced CLI with colored output and interactive features."""
import sys
from typing import Optional
from core.logger import get_logger


class ColorFormatter:
    """Handle colored terminal output."""
    
    def __init__(self, use_colors: bool = True):
        """Initialize color formatter.
        
        Args:
            use_colors: Whether to use colors in output
        """
        self.use_colors = use_colors and self._supports_color()
        self.colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
        }
    
    def _supports_color(self) -> bool:
        """Check if terminal supports colors."""
        return sys.stdout.isatty()
    
    def colorize(self, text: str, color: str) -> str:
        """Apply color to text.
        
        Args:
            text: Text to colorize
            color: Color name from self.colors
            
        Returns:
            Colorized text
        """
        if not self.use_colors or color not in self.colors:
            return text
        return f"{self.colors[color]}{text}{self.colors['reset']}"
    
    def success(self, text: str) -> str:
        """Format success message."""
        return self.colorize(f"✓ {text}", 'green')
    
    def error(self, text: str) -> str:
        """Format error message."""
        return self.colorize(f"✗ {text}", 'red')
    
    def warning(self, text: str) -> str:
        """Format warning message."""
        return self.colorize(f"⚠ {text}", 'yellow')
    
    def info(self, text: str) -> str:
        """Format info message."""
        return self.colorize(f"ℹ {text}", 'blue')
    
    def header(self, text: str) -> str:
        """Format header message."""
        return self.colorize(f"╔═ {text}", 'bold') + self.colorize(" ═" * (50 - len(text)), 'bold')


class ProgressBar:
    """Simple progress bar for terminal output."""
    
    def __init__(self, total: int, width: int = 50):
        """Initialize progress bar.
        
        Args:
            total: Total number of items
            width: Width of progress bar in characters
        """
        self.total = total
        self.width = width
        self.current = 0
        self.formatter = ColorFormatter()
    
    def update(self, increment: int = 1) -> None:
        """Update progress bar.
        
        Args:
            increment: Number of items to increment by
        """
        self.current += increment
        self._draw()
    
    def _draw(self) -> None:
        """Draw progress bar to terminal."""
        if self.total == 0:
            return
        
        percent = self.current / self.total
        filled = int(self.width * percent)
        bar = '█' * filled + '░' * (self.width - filled)
        
        progress_text = f"\r[{bar}] {percent:.1%} ({self.current}/{self.total})"
        sys.stdout.write(progress_text)
        sys.stdout.flush()
        
        if self.current >= self.total:
            sys.stdout.write('\n')
    
    def finish(self) -> None:
        """Ensure progress bar is finished."""
        if self.current < self.total:
            self.current = self.total
            self._draw()


class InteractivePrompts:
    """Interactive prompt utilities."""
    
    def __init__(self, use_colors: bool = True):
        """Initialize interactive prompts.
        
        Args:
            use_colors: Whether to use colors in prompts
        """
        self.formatter = ColorFormatter(use_colors)
    
    def confirm(self, message: str, default: bool = True) -> bool:
        """Ask for user confirmation.
        
        Args:
            message: Prompt message
            default: Default value if user just presses Enter
            
        Returns:
            True if user confirms, False otherwise
        """
        default_str = "Y/n" if default else "y/N"
        prompt = f"{self.formatter.info(message)} [{default_str}]: "
        
        while True:
            response = input(prompt).strip().lower()
            
            if not response:
                return default
            
            if response in ('y', 'yes'):
                return True
            elif response in ('n', 'no'):
                return False
            else:
                print(self.formatter.warning("Please enter 'y' or 'n'"))
    
    def select(self, message: str, options: list, default: Optional[int] = None) -> int:
        """Ask user to select from options.
        
        Args:
            message: Prompt message
            options: List of options to display
            default: Default option index
            
        Returns:
            Selected option index
        """
        print(self.formatter.header(message))
        
        for i, option in enumerate(options, 1):
            default_mark = " (default)" if default is not None and i == default + 1 else ""
            print(f"  {i}. {option}{default_mark}")
        
        while True:
            try:
                prompt = f"\n{self.formatter.info('Select option')} [1-{len(options)}]: "
                response = input(prompt).strip()
                
                if not response and default is not None:
                    return default
                
                selection = int(response) - 1
                if 0 <= selection < len(options):
                    return selection
                else:
                    print(self.formatter.warning(f"Please enter a number between 1 and {len(options)}"))
            except ValueError:
                print(self.formatter.warning("Please enter a valid number"))
    
    def input_text(self, message: str, default: Optional[str] = None) -> str:
        """Ask user for text input.
        
        Args:
            message: Prompt message
            default: Default value
            
        Returns:
            User input
        """
        if default:
            prompt = f"{self.formatter.info(message)} [{default}]: "
        else:
            prompt = f"{self.formatter.info(message)}: "
        
        response = input(prompt).strip()
        return response if response else (default or "")


class CLIOutput:
    """Enhanced CLI output manager."""
    
    def __init__(self, use_colors: bool = True, use_progress: bool = True):
        """Initialize CLI output manager.
        
        Args:
            use_colors: Whether to use colored output
            use_progress: Whether to show progress bars
        """
        self.formatter = ColorFormatter(use_colors)
        self.use_progress = use_progress
        self.logger = get_logger()
    
    def print_header(self, text: str) -> None:
        """Print formatted header.
        
        Args:
            text: Header text
        """
        print(self.formatter.header(text))
    
    def print_success(self, text: str) -> None:
        """Print success message.
        
        Args:
            text: Success message
        """
        print(self.formatter.success(text))
        self.logger.info(text)
    
    def print_error(self, text: str) -> None:
        """Print error message.
        
        Args:
            text: Error message
        """
        print(self.formatter.error(text))
        self.logger.error(text)
    
    def print_warning(self, text: str) -> None:
        """Print warning message.
        
        Args:
            text: Warning message
        """
        print(self.formatter.warning(text))
        self.logger.warning(text)
    
    def print_info(self, text: str) -> None:
        """Print info message.
        
        Args:
            text: Info message
        """
        print(self.formatter.info(text))
        self.logger.info(text)
    
    def create_progress_bar(self, total: int) -> Optional[ProgressBar]:
        """Create progress bar if enabled.
        
        Args:
            total: Total number of items
            
        Returns:
            ProgressBar instance or None
        """
        if self.use_progress:
            return ProgressBar(total)
        return None
    
    def print_table(self, headers: list, rows: list) -> None:
        """Print formatted table.
        
        Args:
            headers: Table headers
            rows: Table rows
        """
        # Calculate column widths
        col_widths = [len(str(header)) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Print header
        header_row = " | ".join(str(header).ljust(width) for header, width in zip(headers, col_widths))
        separator = "-+-".join("-" * width for width in col_widths)
        
        print(self.formatter.header(header_row))
        print(separator)
        
        # Print rows
        for row in rows:
            row_str = " | ".join(str(cell).ljust(width) for cell, width in zip(row, col_widths))
            print(row_str)