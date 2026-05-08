from __future__ import annotations
from abc import ABC, abstractmethod

class State(ABC):
    def __init__(self) -> None:
        self.next_states: list[State] = []

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass

    def check_next(self, next_char: str) -> list[State]:
        return [s for s in self.next_states if s.check_self(next_char)]



class StartState(State):
    def __init__(self): super().__init__()
    def check_self(self, char): return False



class TerminationState(State):
    def __init__(self): super().__init__()
    def check_self(self, char): return False



class DotState(State):
    """
    state for . character (any character accepted)
    """
    def __init__(self): super().__init__()
    def check_self(self, char: str): return True


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """
    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.curr_sym = symbol
    def check_self(self, curr_char: str) -> bool:
        return curr_char == self.curr_sym



class StarState(State):
    def __init__(self, checking_state: State):
        super().__init__()
        self.working_state = checking_state
        self.next_states = [self]
    def check_self(self, char):
        return self.working_state.check_self(char)


class PlusState(State):
    def __init__(self, checking_state: State):
        super().__init__()
        self.working_state = checking_state
        self.next_states = [self]
    def check_self(self, char):
        return self.working_state.check_self(char)


class RegexFSM:
    def __init__(self, regex_expr: str) -> None:
        self.start_state = StartState()
        prev_state = self.start_state
        i = 0
        while i < len(regex_expr):
            char = regex_expr[i]
            next_t = regex_expr[i+1] if i+1 < len(regex_expr) else None
            
            if next_t in ['*', '+']:
                tmp = self.__init_next_state(char, None, None)
                new_state = self.__init_next_state(next_t, prev_state, tmp)
                i += 2
            else:
                new_state = self.__init_next_state(char, prev_state, None)
                i += 1
            
            prev_state.next_states.append(new_state)
            if isinstance(new_state, StarState):
                pass 
            prev_state = new_state
            
        prev_state.next_states.append(TerminationState())

    def __init_next_state(self, next_token: str, prev_state: State, tmp_next_state: State) -> State:
        match next_token:
            case ".": return DotState()
            case "*": return StarState(tmp_next_state)
            case "+": return PlusState(tmp_next_state)
            case _ if next_token.isascii(): return AsciiState(next_token)
        raise AttributeError("Character is not supported")

    def check_string(self, string):
        states = {self.start_state}
        def expand(current):
            res = set(current)
            changed = True
            while changed:
                changed = False
                for s in list(res):
                    for n in s.next_states:
                        if isinstance(n, StarState) and n not in res:
                            res.add(n)
                            changed = True
            return res

        states = expand(states)
        for ch in string:
            next_states = set()
            for s in states:
                for target in s.check_next(ch):
                    next_states.add(target)
            states = expand(next_states)
            if not states: return False
            
        return any(isinstance(n, TerminationState) for s in states for n in s.next_states)
    
if __name__ == "__main__":
    regex_pattern = "a*4.+hi"

    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))  # True
    print(regex_compiled.check_string("meow"))  # False
