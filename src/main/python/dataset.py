
import scipy.misc
import numpy as np

IMAGE_SIZE = 224


def imread(path, target_size=(IMAGE_SIZE,IMAGE_SIZE)):
  # TODO: crop and then resize
  return scipy.misc.imresize(scipy.misc.imread(path, mode='RGB').astype(np.float32), target_size)


def load_tag_data(path):
  tags_to_indices = dict()
  indices_to_tags = dict()
  tag_index = 0
  
  with open(path + 'tag_map.txt', 'r') as tag_map_file:
    for tag in tag_map_file:
      tag = tag.strip()
      tags_to_indices[tag] = tag_index
      indices_to_tags[tag_index] = tag
      tag_index = tag_index+1

  return indices_to_tags, tags_to_indices


def load_raw_data(path):
  # list of scaled source images
  all_images = list()
  # list of tags held by each image
  all_tags = list()
  
  indices_to_tags, tags_to_indices = load_tag_data(path)
  
  with open(path + 'tags.txt', 'r') as tags_file:
    for line in tags_file:
      # Maybe have something to limit # of lines read?
      bits = line.replace('[','').replace(']','').replace(',','').split()
      file_name = bits[0]
      tags = bits[1:]
      all_images.append(imread(path + file_name))
      all_tags.append(tags)
  
  tag_labels = list()
  for tags in all_tags:
    row = np.zeros(len(indices_to_tags), dtype = np.float32)
    for tag in tags:
      row[tags_to_indices[tag]] = 1
    tag_labels.append(row)

  return np.array(all_images, dtype = np.float32), np.array(tag_labels), indices_to_tags


def load_data(path = None, validation_fraction = .25):
  """ load data 
  Args:
    validation_fraction: fraction of data to use for validation & testing
    test_fraction: fraction of validation_data to use as the "test" category
  Returns:
    train_data, validation_data
  """
  
  if not path:
    path = '../../../output/'
  
  images, labels, indices_to_tags = load_raw_data(path)
  
  count = len(images)
  validation_count = int(count * validation_fraction)
  train_count = count - validation_count
  
  return (DataSet(images[:train_count], labels[:train_count]),
          DataSet(images[train_count:], labels[train_count:]),
          indices_to_tags)


class DataSet(object):
  def __init__(self, images, labels):
    self._images = images
    self._labels = labels
    self._epochs_completed = 0
    self._index_in_epoch = 0
    self._num_examples = images.shape[0]
  
  @property
  def images(self):
    return self._images

  @property
  def labels(self):
    return self._labels
  
  @property
  def num_examples(self):
    return self._num_examples

  @property
  def epochs_completed(self):
    return self._epochs_completed

  def next_batch(self, batch_size):
    """Return the next `batch_size` examples from this data set."""
    start = self._index_in_epoch
    self._index_in_epoch += batch_size
    if self._index_in_epoch > self._num_examples:
      # Finished epoch
      self._epochs_completed += 1
      # Shuffle the data
      perm = np.arange(self._num_examples)
      np.random.shuffle(perm)
      self._images = self._images[perm]
      self._labels = self._labels[perm]
      # Start next epoch
      start = 0
      self._index_in_epoch = batch_size
      assert batch_size <= self._num_examples
    end = self._index_in_epoch
    return self._images[start:end], self._labels[start:end]

