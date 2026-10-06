#include <malloc.h>
#include <stdlib.h>

/* Samba's ptr_overflow rejects Android's tagged heap addresses during
 * NTLM parsing. Apply only to the Samba process; remove when upstream fixes it.
 */
__attribute__((constructor)) static void disable_heap_tagging(void)
{
    if (!mallopt(M_BIONIC_SET_HEAP_TAGGING_LEVEL, M_HEAP_TAGGING_LEVEL_NONE)) {
        abort();
    }
}
