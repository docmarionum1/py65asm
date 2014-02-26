var = $99

		.org $C000
start	lda #$ff
		jmp start

		.org $fffd
		.byte var
		.word start
