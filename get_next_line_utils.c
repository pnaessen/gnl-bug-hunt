#include "get_next_line.h"

char	*ft_strdup(const char *s)
{
	size_t	len;
	char	*str;
	size_t	i;

	i = 0;
	len = 0;
	while (s[len])
		len++;
	str = malloc(len + 1);
	if (!str)
		return (NULL);
	if (len == 0)
		return (malloc(1));
	while (i < len)
	{
		str[i] = s[i];
		i++;
	}
	str[i] = '\0';
	return (str);
}

char	*ft_strjoin(char *s1, char *s2)
{
	size_t	len1;
	size_t	len2;
	char	*str;

	len2 = 0;
	if (!s1 || !s2)
		return (NULL);
	len1 = ft_strlen(s1);
	while (s2[len2] != '\n' && s2[len2] != '\0')
		len2++;
	str = malloc(len1 + len2);
	if (!str)
		return (NULL);
	ft_memcpy(str, s1, len1);
	ft_memcpy(str + len1, s2, len2);
	str[len1 + len2] = '\0';
	return (str);
}

void	ft_update(char *str)
{
	int	i;
	int	j;

	j = 0;
	i = 0;
	while (str[i] && str[i++] != '\n')
		;
	while (str[i])
		str[j++] = str[i++];
}

size_t	ft_strlen(const char *s)
{
	int	i;

	i = 0;
	while (s[i])
		i++;
	return (i);
}

void	*ft_memcpy(void *dst, const void *src, size_t n)
{
	unsigned char	*d;
	unsigned char	*s;
	size_t			i;

	i = 0;
	d = (unsigned char *)dst;
	s = (unsigned char *)src;
	if (d == s)
		return (dst);
	while (i < n)
	{
		d[i] = s[i];
		i++;
	}
	return (dst);
}
