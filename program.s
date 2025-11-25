	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
.set @feat.00, 0
	.file	"<string>"
	.def	main;
	.scl	2;
	.type	32;
	.endef
	.text
	.globl	main
	.p2align	4
main:
.seh_proc main
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	pushq	%rax
	.seh_stackalloc 8
	movq	%rsp, %rbp
	.seh_setframe %rbp, 0
	.seh_endprologue
	movl	$0, 4(%rbp)
	subq	$32, %rsp
	leaq	.str4725515630691834611(%rip), %rcx
	leaq	.str4918782734983268285(%rip), %rdx
	callq	printf
	xorl	%ecx, %ecx
	callq	fflush
	leaq	.str5030970306535922903(%rip), %rcx
	leaq	4(%rbp), %rdx
	callq	scanf
	addq	$32, %rsp
	cmpl	$11, 4(%rbp)
	jl	.LBB0_2
	subq	$32, %rsp
	leaq	.str4725515630691834611(%rip), %rcx
	leaq	.str7262352148376039936(%rip), %rdx
	jmp	.LBB0_3
.LBB0_2:
	subq	$32, %rsp
	leaq	.str4725515630691834611(%rip), %rcx
	leaq	.str5726306198114121776(%rip), %rdx
.LBB0_3:
	callq	printf
	xorl	%ecx, %ecx
	callq	fflush
	addq	$32, %rsp
	movl	$16, %eax
	callq	__chkstk
	subq	%rax, %rsp
	movq	%rsp, %rbx
	movl	$0, (%rbx)
	leaq	.str4725515630691834611(%rip), %rsi
	leaq	.str184026520705037517(%rip), %rdi
	.p2align	4
.LBB0_4:
	movl	(%rbx), %eax
	cmpl	4(%rbp), %eax
	jge	.LBB0_6
	subq	$32, %rsp
	movq	%rsi, %rcx
	movq	%rdi, %rdx
	callq	printf
	xorl	%ecx, %ecx
	callq	fflush
	addq	$32, %rsp
	incl	(%rbx)
	jmp	.LBB0_4
.LBB0_6:
	subq	$32, %rsp
	leaq	.str4725515630691834611(%rip), %rcx
	leaq	.str1220705876898242704(%rip), %rdx
	callq	printf
	xorl	%ecx, %ecx
	callq	fflush
	addq	$32, %rsp
	xorl	%eax, %eax
	leaq	8(%rbp), %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	retq
	.seh_endproc

	.section	.rdata,"dr"
	.globl	.str4918782734983268285
	.p2align	4, 0x0
.str4918782734983268285:
	.asciz	"Escribe un numero: "

	.globl	.str4725515630691834611
.str4725515630691834611:
	.asciz	"%s\n"

	.globl	.str5030970306535922903
.str5030970306535922903:
	.asciz	"%d"

	.globl	.str7262352148376039936
	.p2align	4, 0x0
.str7262352148376039936:
	.asciz	"Tu numero es mayor que 10."

	.globl	.str5726306198114121776
	.p2align	4, 0x0
.str5726306198114121776:
	.asciz	"Tu numero es 10 o menos."

	.globl	.str184026520705037517
.str184026520705037517:
	.asciz	"je"

	.globl	.str1220705876898242704
	.p2align	4, 0x0
.str1220705876898242704:
	.asciz	"Conteo finalizado."

