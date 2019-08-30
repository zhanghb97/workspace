#include <stdio.h>
#include <stdlib.h>

int* twoSum(int* nums, int numsSize, int target, int* returnSize);

int main(int argc, char const *argv[]) {
  int nums[4] = {2, 7, 11, 15};
  int size = 0;
  int *p;
  p = twoSum(nums, 4, 9, &size);
  for (int i = 0; i < 2; i++) {
    printf("%d\n", *(p + i));
  }
  return 0;
}
/**
 * Note: The returned array must be malloced, assume caller calls free().
 */
int* twoSum(int* nums, int numsSize, int target, int* returnSize) {
  // Malloc the return array.
  int *array;
  array = (int *)malloc(2 * sizeof(int));
  // Find the answer with two for loop.
  for (int i = 0; i < numsSize - 1; i++) {
    for (int j = i + 1; j < numsSize; j++) {
      int result = *(nums + i) + *(nums + j);
      // If the result matches the target, return the array.
      if (result == target) {
        // Return
        array[0] = i;
        array[1] = j;
      }
    }
  }
  *returnSize = 2;
  return array;
}
