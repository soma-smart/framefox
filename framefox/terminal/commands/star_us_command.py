import subprocess
import webbrowser

from framefox.terminal.commands.abstract_command import AbstractCommand

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen & LEUROND Raphael
Github: https://github.com/RayenBou
Github: https://github.com/Vasulvius
"""


class StarUsCommand(AbstractCommand):
    """
    Command to star the Framefox project on GitHub.

    This command opens the GitHub repository page to allow users to easily
    star the project and show their support.
    """

    GITHUB_REPO_URL = "https://github.com/soma-smart/framefox"

    def __init__(self):
        """Initialize the star-us command."""
        super().__init__("star-us")

    def execute(self):
        """
        Star the Framefox project on GitHub

        Attempts to star the repository using GitHub CLI (gh) if available,
        otherwise falls back to opening the repository in the browser.
        """
        self.printer.print_msg(
            "🌟 Thank you for supporting Framefox!",
            theme="success",
            linebefore=True,
        )

        if self._try_star_with_gh_cli():
            return 0

        return self._fallback_to_browser()

    def _try_star_with_gh_cli(self) -> bool:
        try:
            result = subprocess.run(["gh", "--version"], capture_output=True, text=True, timeout=5)

            if result.returncode != 0:
                self.printer.print_msg(
                    "GitHub CLI (gh) not found. Install it for direct starring!",
                    theme="warning",
                )
                return False

            auth_result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, timeout=5)

            if auth_result.returncode != 0:
                self.printer.print_msg(
                    "🔐 Please login to GitHub CLI first: gh auth login",
                    theme="warning",
                )
                return False

            self.printer.print_msg(
                "🔧 Using GitHub CLI to star the repository...",
                theme="info",
            )

            check_result = subprocess.run(["gh", "api", "user/starred/soma-smart/framefox"], capture_output=True, text=True, timeout=10)

            if check_result.returncode == 0:
                self.printer.print_msg(
                    "⭐ You have already starred this repository!",
                    theme="success",
                )
                self.printer.print_msg(
                    "Thank you for your continued support! 🦊",
                    theme="info",
                )
                return True

            star_result = subprocess.run(
                ["gh", "api", "-X", "PUT", "user/starred/soma-smart/framefox"], capture_output=True, text=True, timeout=10
            )

            if star_result.returncode == 0:
                self.printer.print_msg(
                    "⭐ Successfully starred Framefox on GitHub!",
                    theme="success",
                )
                self.printer.print_msg(
                    "Your support helps us improve Framefox! 🦊",
                    theme="info",
                )
                return True
            else:
                self.printer.print_msg(
                    "❌ Failed to star repository via GitHub CLI",
                    theme="warning",
                )
                return False

        except subprocess.TimeoutExpired:
            self.printer.print_msg(
                "⏱️ GitHub CLI operation timed out",
                theme="warning",
            )
            return False
        except FileNotFoundError:
            self.printer.print_msg(
                "GitHub CLI (gh) not found. Install it for direct starring!",
                theme="warning",
            )
            return False
        except Exception as e:
            self.printer.print_msg(
                f"❌ Error using GitHub CLI: {str(e)}",
                theme="error",
            )
            return False

    def _fallback_to_browser(self) -> int:
        self.printer.print_msg(
            "🌐 Opening GitHub repository in your browser...",
            theme="info",
        )

        try:
            webbrowser.open(self.GITHUB_REPO_URL)

            self.printer.print_msg(
                f"✨ Please star us at: {self.GITHUB_REPO_URL}",
                theme="success",
            )

            self.printer.print_msg(
                "Your support helps us improve Framefox! 🦊",
                theme="info",
            )

            return 0

        except Exception as e:
            self.printer.print_msg(
                f"❌ Could not open browser: {str(e)}",
                theme="error",
            )

            self.printer.print_msg(
                f"Please manually visit: {self.GITHUB_REPO_URL}",
                theme="info",
            )

            return 1

    def get_name(self) -> str:
        """Get the command name"""
        return "star-us"
