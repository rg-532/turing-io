"""This module defines the base classes for nodes in the pipeline:

    - :class:`PipelineSource` defines what is required from any source lexer that is used in the pipeline.

    - :class:`PipelineComponent` extends the above to define how a component in the pipeline should be implemented.
      A pipeline component is used to transform a given stream of tokens.
"""
from abc import ABC, abstractmethod
from collections import deque
from typing import TypeVar, Optional, Any

from compiler.frontend.lexer.base_lexer import BaseLexer
from compiler.frontend.lexer.pipeline.core.token_ import PipelineTokenProto

T_PipelineToken = TypeVar("T_PipelineToken", bound=PipelineTokenProto)


class PipelineSource(BaseLexer[T_PipelineToken], ABC):
    """Defines an interface + initialization for a **pipeline source**, which sits at the bottom of a pipeline and
    serves as a source of :class:`PipelineToken` objects.

    This abstract base extends/alters the basic :class:`BaseLexer` interface in the following ways:
        - Binds the generic type of tokens which are generated to some implementation of :class:`PipelineToken`.
        - Adds the ``make_token()`` method which allows creation of new tokens.
        - Adds the ``clone_token()`` method which makes a proper copy of a given token.
    """
    @abstractmethod
    def token(self) -> T_PipelineToken:
        ...

    @abstractmethod
    def is_terminal_token(self, tok: T_PipelineToken) -> bool:
        ...

    @abstractmethod
    def new_token(
            self, type_: Optional[str] = None, value: Any = None,
            lineno: Optional[int] = None, colno: Optional[int] = None,
            e_lineno: Optional[int] = None, e_colno: Optional[int] = None
    ) -> T_PipelineToken:
        """Makes a new token with the given parameters as its attributes."""
        ...


class PipelineComponent(PipelineSource[T_PipelineToken], ABC):
    """Defines an interface + initialization for a **pipeline component**, which serves as an object that wraps some
    base lexer and alters its output stream in some way.

    For complex altering schemes which use lookahead and do not necessarily map inputs to outputs with a one-to-one
    mapping, the pipeline component uses an **output queue** which yields the outputted stream.

    Additionally, to support lookaheads, this class defines a **feedback queue**, into which tokens which were fetched
    but still need some processing can be pushed and re-fetched later. This is relevant when for component desiring
    to use lookahead but not emit it out yet.

    Note that the source base lexer is **private**, meaning it shouldn't be accessed by subclasses. Instead, to
    get tokens subclasses are required to call ``next_input_token()`` integrates the feedback queue into the input
    stream.

    The reasoning behind the dual-queue approach can be found in ``DEV_LOG.md`` (November 26th, 2025).

    Finally, note that this class implements the required ``input()`` and ``token()`` instance methods that
    :class:`BaseLexer` requires, which interact with these queues as described.

    See the ``token()`` method for a complete flow showcasing how and when these queues are used, and the ``process()``
    abstract method's description for explanation on how a concrete component should insert tokens into these queues.

    Attributes:
        feedback_queue: Queue for storing lookahead tokens and tokens needing further processing.
                        This queue precedes the source lexer, meaning tokens fetched from it are processed first.
        output_queue:   Queue defining the output stream of this component.
    """
    def __init__(self, source_lexer: PipelineSource[T_PipelineToken]) -> None:
        self.__source: PipelineSource[T_PipelineToken] = source_lexer
        self.feedback_queue: deque[T_PipelineToken] = deque()
        self.output_queue: deque[T_PipelineToken] = deque()

    @abstractmethod
    def process(self, tok: T_PipelineToken) -> None:
        """Processes a token from ``__source``, and inserts the result into ``output_queue``.

        Note that the received token can be ``None`` and that this may insert ``None`` to signal termination of lexing.

        Further, this method may insert tokens into ``feedback_queue`` to store tokens which need further processing.
        This queue precedes ``__source``, meaning that tokens from it are fetched and sent here before the next token
        from ``__source``. This is very useful when utilizing lookahead.

        :param tok: Token to process.

        NOTE:
            If the ``__source`` lexer outputted ``None``, signaling its termination, the ``None`` value is still sent
            here, and this method must insert ``None`` into ``output_queue`` to properly signal termination of itself.

            Not inserting ``None`` at any point will likely result in an infinite loop!
        """
        ...

    def input(self, text: str) -> None:
        self.__source.input(text)
        self.feedback_queue.clear()
        self.output_queue.clear()

    def token(self) -> T_PipelineToken:
        """Returns the next token, or ``None`` if there is no next token.

        This implementation of ``token()`` returns tokens popped from ``output_queue`` only, with its logic being
        as follows:
            1. If ``output_queue`` is not empty, pop and return a token from it (stop).
                1.1. This token can be ``None``, effectively signaling termination.
            2. Otherwise, gets the next input token by calling ``next_input_token()`. processes it, and returns
               to step 1.

        :return:    Next token.
        """
        while len(self.output_queue) == 0:     # Output queue empty
            self.process(self.next_input_token())

        return self.output_queue.popleft()

    def is_terminal_token(self, tok: T_PipelineToken) -> bool:
        return self.__source.is_terminal_token(tok)

    def new_token(
            self, type_: Optional[str] = None, value: Any = None,
            lineno: Optional[int] = None, colno: Optional[int] = None,
            e_lineno: Optional[int] = None, e_colno: Optional[int] = None
    ) -> T_PipelineToken:
        return self.__source.new_token(type_, value, lineno, colno, e_lineno, e_colno)

    def next_input_token(self) -> T_PipelineToken:
        """Helper method which returns the next token to process.

        More specifically:
            - If ``feedback_queue`` is not empty, fetches the next token from it.
            - Otherwise, fetches a token by calling ``__source.token()``.
            - Returns whatever token it fetched.

        :return:    Next token for processing.
        """
        if len(self.feedback_queue) > 0:
            tok = self.feedback_queue.popleft()
        else:
            tok = self.__source.token()

        return tok
