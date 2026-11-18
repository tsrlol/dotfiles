" Godot's own language server: real parse errors, type errors and warnings.
" It only answers while the Godot editor has the project open, or while a
" headless one runs: godot --headless --editor --lsp-port 6005 --path game
let s:address = '127.0.0.1:6005'
let s:probe = {'time': 0, 'up': 0}

" ALE's Neovim socket code catches only an older error message, so a refused
" connection surfaces as an error every time a .gd buffer is linted. Probing
" first and returning no project root makes ALE skip the linter quietly.
" The result is cached briefly because ALE asks on every lint.
function! s:ServerUp() abort
    if !has('nvim')
        return 1
    endif

    if localtime() - s:probe.time < 5
        return s:probe.up
    endif

    let s:probe.time = localtime()

    try
        call chanclose(sockconnect('tcp', s:address))
        let s:probe.up = 1
    catch
        let s:probe.up = 0
    endtry

    return s:probe.up
endfunction

function! ale_linters#gdscript#godot#ProjectRoot(buffer) abort
    let l:project = ale#path#FindNearestFile(a:buffer, 'project.godot')

    if empty(l:project) || !s:ServerUp()
        return ''
    endif

    return fnamemodify(l:project, ':h')
endfunction

call ale#linter#Define('gdscript', {
\   'name': 'godot',
\   'lsp': 'socket',
\   'address': s:address,
\   'project_root': function('ale_linters#gdscript#godot#ProjectRoot'),
\})
