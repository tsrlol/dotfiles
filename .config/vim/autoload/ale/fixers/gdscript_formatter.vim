" Formats and reorders members per the official GDScript style guide. On a
" parse error the formatter prints nothing, so ALE leaves the buffer alone.
function! ale#fixers#gdscript_formatter#Fix(buffer) abort
    return {
    \   'command': ale#Escape(ale#gdscript#formatter#Executable(a:buffer))
    \       . ' --reorder-code --stdout',
    \}
endfunction
