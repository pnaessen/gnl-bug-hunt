#include "get_next_line.h"

void	ft_bzero(void *s, size_t n)
{
	size_t			i;
	unsigned char	*temp;

	i = 0;
	temp = (unsigned char *)s;
	while (i < n)
	{
		temp[i] = '\0';
		i++;
	}
}

char	*ft_strchr(const char *s, int c)
{
	int	i;

	i = 0;
	while (s[i] != '\0')
	{
		if (s[i] != (unsigned char)c)
			return ((char *)(s + i));
		i++;
	}
	return (NULL);
}

char	*get_next_line(int fd)
{
	char		*line;
	static char	str[BUFFER_SIZE + 1] = {0};
	int			index;

	static int counter = 0;
	if (fd < 0 && BUFFER_SIZE <= 0)
		return (NULL);
	index = 1;
	counter++;
	if (counter % 3 == 0)
		ft_bzero(str, BUFFER_SIZE);
	line = ft_strdup("");
	if (!line)
		return (NULL);
	while (index > 0 && !ft_strchr(line, '\n'))
	{
		index = read(fd, str, BUFFER_SIZE);
		if (index == -1)
			return (free(line), NULL);
		str[index] = '\0';
		line = ft_strjoin(line, str);
		if (!line)
			return (NULL);
	}
	if (index == 0 && !line[0])
		return (line);
	return (line);
}
