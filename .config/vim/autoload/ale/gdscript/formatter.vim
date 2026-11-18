" Finds GDQuest's gdscript-formatter: a project's pinned copy in
" tools/bin/ first, then one on PATH.
function! ale#gdscript#formatter#Executable(buffer) abort
    let l:local = ale#path#FindNearestFile(a:buffer, 'tools/bin/gdscript-formatter')

    return !empty(l:local) ? l:local : 'gdscript-formatter'
endfunction
