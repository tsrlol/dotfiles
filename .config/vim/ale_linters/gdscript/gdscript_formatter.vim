" Style lint from GDQuest's gdscript-formatter, read from stdin so it runs
" as you type. Output lines look like: stdin:5:max-line-length:warning: msg
function! ale_linters#gdscript#gdscript_formatter#Handle(buffer, lines) abort
    let l:pattern = '\v^stdin:(\d+):([^:]+):(\w+): (.*)$'
    let l:output = []

    for l:match in ale#util#GetMatches(a:lines, l:pattern)
        call add(l:output, {
        \   'lnum': l:match[1] + 0,
        \   'code': l:match[2],
        \   'type': l:match[3] is# 'error' ? 'E' : 'W',
        \   'text': l:match[4],
        \})
    endfor

    return l:output
endfunction

call ale#linter#Define('gdscript', {
\   'name': 'gdscript_formatter',
\   'executable': function('ale#gdscript#formatter#Executable'),
\   'command': '%e lint',
\   'callback': 'ale_linters#gdscript#gdscript_formatter#Handle',
\})
